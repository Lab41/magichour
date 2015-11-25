from __future__ import division
from collections import defaultdict
from math import floor, sqrt, log10

from utils import *

class Cluster:
    def __init__(self, leaf):
        self.leafs = []
        self.leafs.append(leaf)
        self.template_line = leaf.get_template_line()

    def check_for_match(self, line, threshold, skip_count):
        '''
        Check to see if input line belongs in the cluster
        '''
        # Matching only needs to check for similarity to template line
        if cosine_sim(self.template_line, line, skip_count) >= threshold:
            return True
        else:
            return False

    def add_to_leaf(self, line, threshold, skip_count):
        '''
        Add line to this cluster
        '''
        leaf_indexes_that_match = []
        for i in range(len(self.leafs)):
            if self.leafs[i].check_for_match(line, threshold, skip_count):
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
            print line
            print self.template_line
            print len(self.leafs)
            raise ValueError("Received %d matches, 1 or 2 expected"%len(leaf_indexes_that_match))

    def get_template_line(self):
        return self.template_line

    def get_num_lines(self):
        num_msgs = 0
        for leaf in self.leafs:
            num_msgs += leaf.get_num_lines()
        return num_msgs

    def print_template_lines(self):
        for leaf in self.leafs:
            print leaf.get_num_lines(), leaf.get_template_line()

    def split_leaf(self, min_items_for_split, skip_count, min_word_pos_entropy, min_percent):
        replacements = [] # tuple of (index_to_delete, [new_leafs])
        for i, leaf in enumerate(self.leafs):
            if leaf.get_num_lines() > min_items_for_split:
                replacement_leafs = leaf.split_leaf(skip_count, min_word_pos_entropy, min_percent)
                if replacement_leafs is not None: # If every item is the same
                    replacements.append((i, replacement_leafs))

        # IMPORTANT: Reverse replacements so that deletions don't change indexes
        replacements.reverse()

        for index_to_delete, new_leafs in replacements:
            del self.leafs[index_to_delete]
            self.leafs.extend(new_leafs)
