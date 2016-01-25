from __future__ import division
from collections import defaultdict
from math import floor, sqrt, log10
from time import mktime

from cluster import Cluster
from utils import *


class Leaf(object):
    def __init__(self, log_line, index=None, index_val=None):
        self.log_lines = []
        self.log_lines.append(log_line)
        self.template_line = log_line.text
        self.template_line_split = log_line.text.split()
        self.index = index
        self.index_val = index_val

    def check_for_match(self, line_split, threshold, skip_count, verbose=False):
        if cosine_sim(self.template_line_split, line_split, skip_count) >= threshold:
            #print cosine_sim(self.template_line, line, skip_count)
            #print line
            #print self.template_line
            if self.index is None:
                #print 1
                return True # Case: We are just matching the whole line
            else: # We need to check a specific spot to see if it matches
                if self.index_val is None:
                    #print 2
                    return True # Case: The "other" category
                elif len(line_split) > self.index + skip_count and \
                                self.index_val == line_split[skip_count + self.index]:
                    #print 3
                    return True # Case: Match in the specific leaf
                else:
                    #print 4
                    return False # Case: Similar log line but not the correct value in index position
        else:
            return False

    def add_to_leaf(self, line, threshold, skip_count):
        self.log_lines.append(line)

    def get_template_line(self):
        return self.template_line

    def get_num_lines(self):
        return len(self.log_lines)

    def print_template_lines(self, indent):
        print '--'*indent, self.get_num_lines(), self.index_val#, self.get_template_line()

    def print_groups(self, index, include_text=False):
        for line in self.log_lines:
            try:
                if include_text:
                    print '%s,%d,%s'%(mktime(line.ts.timetuple()), index, line.text)
                else:
                    print '%s,%d,%s'%(mktime(line.ts.timetuple()), index)
            except:
                print ',%d'%(index)
        return index + 1

    def split_leaf(self, min_items_for_split, skip_count, min_word_pos_entropy, min_percent, verbose=False):
        '''
        Split this leaf into multiple leaves

        TODO: This function is gross clean it up!
        '''

        if self.get_num_lines() < min_items_for_split:
            return None

        # use line length of first line as a hack for max line length
        line_length = max([len(self.log_lines[i].text.split()) for i in range(len(self.log_lines))])
        # Build position dependent word counter
        word_counts = [defaultdict(int) for i in range(line_length)]

        # Count words in each line
        for line in self.log_lines:
            for i, word in enumerate(line.text.split()[skip_count:]):
                word_counts[i][word] += 1

        # Calculate entropies for each word position
        entropies = get_entropy_of_word_positions(word_counts, len(self.log_lines))

        # Get minimum, non-zero entropy
        min_entropy = 1e9
        min_entropy_index = None
        for i, entropy in enumerate(entropies):
            if entropy < min_entropy and entropy >= min_word_pos_entropy:
                min_entropy_index = i
                min_entropy = entropy

        if min_entropy_index == None:
            # Every entropy is zero, can't split
            return None

        # Iterate through words in the position with the least entropy and see if they have a sufficient percentage
        split_words = set()
        min_word_occurrence = floor(min_percent * len(self.log_lines))
        for word in word_counts[min_entropy_index]:
            if word_counts[min_entropy_index][word] > min_word_occurrence:
                split_words.add(word)

        if len(split_words) == 0:
            # Cluster not splittable
            return None # TODO: Think about how to avoid checking this leaf every time?
            #print min_word_occurrence, word_counts[min_entropy_index]
            #raise ValueError("Need at least one canddiate word to split on, only got %d"%len(split_words))

        # Add log lines to leaves
        leafs = {}
        for line in self.log_lines:
            line_split = line.text.split()[skip_count:]
            try:
                split_word = line_split[min_entropy_index]
            except:
                split_word = None # Handle the case where the field with the min entropy is at the end of the line

            if split_word not in split_words:
                split_word = None # Handle the other case

            if split_word not in leafs:
                # If this is a new word we are supposed to create a leaf for, create that leaf
                leafs[split_word] = Leaf(line, index=min_entropy_index, index_val=split_word)
            else:
                # We are adding this line to an existing cluster
                leafs[split_word].add_to_leaf(line, None, None) # Threshold and skip count don't matter here?

        # Make sure to add other to avoid trouble later
        split_word = None
        if split_word not in leafs:
            leafs[split_word] = Leaf(line, index=min_entropy_index, index_val=split_word)

        if verbose:
            print "Splitting Leaf: ", split_words
        cluster = None
        for word in leafs:
            if cluster is None:
                cluster = Cluster(leafs[word], index=min_entropy_index, index_val=None)
            else:
                cluster.add_leaf(leafs[word])
        return cluster #[leafs[word] for word in leafs]

