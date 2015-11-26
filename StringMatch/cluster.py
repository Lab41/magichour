from __future__ import division
from collections import defaultdict
from math import floor, sqrt, log10

from utils import *

class Cluster(object):
    def __init__(self, leaf, index=None, index_val=None):
        self.leafs = []
        self.leafs.append(leaf)
        self.template_line = leaf.get_template_line()
        self.template_line_split = self.template_line.split()
        self.index = index
        self.index_val = index_val

    def add_leaf(self, leaf):
        self.leafs.append(leaf)

    def check_for_match(self, line_split, threshold, skip_count, verbose=False):
        '''
        Check to see if input line belongs in the cluster
        '''
        if cosine_sim(self.template_line_split, line_split, skip_count) >= threshold:
            if self.index is not None and self.index_val is not None:
                if len(line_split) > skip_count + self.index and  self.index_val != line_split[skip_count + self.index]:
                    if verbose:
                        print 'failed selfcheck'
                    return False
                else:
                    if verbose:
                        print 'passed selfcheck'

            for leaf in self.leafs:
                if leaf.check_for_match(line_split, threshold, skip_count):
                    return True

        return False

    def add_to_leaf(self, line, threshold, skip_count):
        '''
        Add line to this cluster
        '''
        line_split = line.split()
        leaf_indexes_that_match = []
        for i in range(len(self.leafs)):
            if self.leafs[i].check_for_match(line_split, threshold, skip_count):
                leaf_indexes_that_match.append(i)

        if len(leaf_indexes_that_match) == 1:
            ind = leaf_indexes_that_match[0]
            self.leafs[ind].add_to_leaf(line, threshold, skip_count)
        elif len(leaf_indexes_that_match) == 2:
            # Preference is to match the non "other" leaf
            if self.leafs[leaf_indexes_that_match[0]].index_val is not None:
                self.leafs[leaf_indexes_that_match[0]].add_to_leaf(line, threshold, skip_count)
            else:
                self.leafs[leaf_indexes_that_match[1]].add_to_leaf(line, threshold, skip_count)
        else:
            ls = line.split()[skip_count:]
            print 'Input Line: ', ls
            #print 'Cluster template: ', self.template_line
            for leaf_index in leaf_indexes_that_match:
                leaf = self.leafs[leaf_index]
                print 'leaf: ', type(leaf), leaf.index, leaf.index_val, \
                      leaf.check_for_match(line_split, threshold, skip_count, verbose=True), ' '.join(leaf.get_template_line().split()[skip_count:])
            #print len(self.leafs)
            raise ValueError("Received %d matches, 1 or 2 expected"%len(leaf_indexes_that_match))

    def get_template_line(self):
        return self.template_line

    def get_num_lines(self):
        num_msgs = 0
        for leaf in self.leafs:
            num_msgs += leaf.get_num_lines()
        return num_msgs

    def print_template_lines(self, indent):
        print '--'*indent, self.get_num_lines(), self.index_val, self.get_template_line()
        for leaf in self.leafs:
            leaf.print_template_lines(indent + 4)
            #print leaf.get_num_lines(), leaf.get_template_line()

    def split_leaf(self, min_items_for_split, skip_count, min_word_pos_entropy, min_percent):
        replacements = [] # tuple of (index_to_delete, [new_leafs])
        for i, leaf in enumerate(self.leafs):
            if leaf.get_num_lines() > min_items_for_split:
                replacement_leafs = leaf.split_leaf(min_items_for_split, skip_count, min_word_pos_entropy, min_percent)
                if replacement_leafs is not None: # If every item is the same
                    replacements.append((i, replacement_leafs))

        # IMPORTANT: Reverse replacements so that deletions don't change indexes
        replacements.reverse()

        for index_to_delete, new_leafs in replacements:
            print 'New Leafs:'
            for leaf in new_leafs.leafs:
                print leaf.get_num_lines(), leaf.get_template_line()
            print '---------'

            if self.leafs[index_to_delete].index_val is not None:
                new_leafs.index_val = self.leafs[index_to_delete].index_val
                new_leafs.index = self.leafs[index_to_delete].index

            del self.leafs[index_to_delete]
            self.add_leaf(new_leafs)
            #self.leafs.extend(new_leafs)
