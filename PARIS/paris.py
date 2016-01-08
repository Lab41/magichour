from __future__ import division
import random
from math import floor
from collections import Counter, defaultdict
from itertools import combinations
from copy import deepcopy

#alphabet_size = 200
alphabet_size = 194
#num_elements_per_atom = 8
num_elements_per_atom = 40

num_K = 50 # Number of atoms
L = 3 # number of atoms in dataset
N = 300 # 3000 # Number of sets
r = 1#.51
r_count = int(floor(r*num_elements_per_atom))
r_slack = num_elements_per_atom - r_count

#print num_K,L,N,r, r_count, r_slack

def xor(s1, s2, skip_in_s2=0):
    """
    XOR at the core of the the PARIS distance function
    Take in two sets and compute their symmetric difference. Allow up to skip_in_s2 items to be missing.
    """
    num_in_s1_not_in_s2 = len(s1.difference(s2))
    num_in_s2_not_in_s1 = len(s2.difference(s1))

    num_in_s2_not_in_s1 -= skip_in_s2
    num_in_s2_not_in_s1 = max(num_in_s2_not_in_s1, 0)
    return num_in_s1_not_in_s2  + num_in_s2_not_in_s1

def paris_distance(di, A, R, r_count):
    '''
    Compute paris distance function
    '''
    if len(di) == 0:
        return 0
    total_rep = set()
    for ind in R:
        total_rep.update(A[ind])


    return xor(di, total_rep, r_count)/len(di)

def PCF(D, A, R, tau=.5, verbose=False):
    '''
    Calculate the full PARIS cost function given a set of Documents, Atoms, and a representation
    '''
    if verbose:
        print 'PCF:'
        print '   A: ', len(A)#[sorted(a) for a in A]
        print '   R: ', len([1 for item in R if len(item) > 0])
        print '   D/R:', len(D), len(R)
        print '   r_count:', r_slack
    pcfa = 0
    pcfb = 0
    for ind in range(len(D)):
        # PCFA
        pcfa += paris_distance(D[ind], A, R[ind], r_slack)

        # PCFB
        if len(D[ind]) != 0:
            #pcfb += float(len(R[ind]))/len(D[ind])
            pcfb += float(len([w for i in R[ind] for w in A[i]]))/len(D[ind])
    if verbose:
       print 'PCFA:', pcfa
       print 'PCFB:', pcfb

    # PCFC
    pcfc = tau*len(A)

    total_cost = 5*pcfa + pcfb + pcfc
    if verbose:
        print 'PCFC:', tau*len(A)
        print 'TOTAL: ', total_cost
    return total_cost


def get_best_representation(di, A, verbose=False):
    '''
    Get best possible representation for di given a set of atoms A
    '''
    # Start with empty set for this representation
    curr_r = set()

    # degenerate case
    if len(di)  == 0:
        return curr_r

    min_atom_ind =-1
    min_distance = paris_distance(di, A, curr_r, r_slack) + 1.0/len(di)*len(curr_r)
    # Keep adding atoms to the representation until we are unable to improve the result
    while min_atom_ind is not None:
        # Find atom to add to the representation that minimizes total distance
        min_atom_ind = None
        for i in range(len(A)):
            # Only check distance for items where there is some intersection between the line and the atom
            if i not in curr_r and len(di.intersection(A[i])) > 0:
                attempted_r = deepcopy(curr_r)
                attempted_r.add(i)
                dist = paris_distance(di, A, attempted_r, r_slack) + 1.0/len(di)*len(attempted_r)
                if verbose:
                    print 'Dist, min_dist', dist, min_distance
                if min_distance is None or dist < min_distance:
                    min_distance = dist
                    min_atom_ind = i

        if min_atom_ind is not None:
            curr_r.add(min_atom_ind)
    return curr_r

def design_atom(E):
    '''
    Implementation of the atom design function described in the PARIS paper

    '''
    # Get most common pair of elements in E
    c = Counter()
    for ind in range(len(E)):
        c.update(combinations(E[ind], 2))

    if len(c) == 0:
        # There are no item pairs so we can't use our design atom function here
        return None

    Aj = None
    # Initial atom is the most common pair of atoms in E
    Aj_next = set(c.most_common(1)[0][0])

    # Baseline error as the error in the current error set
    prev_el = PCF(E, [Aj], [set() for ind in range(len(E))]) # Empty representation set

    # Compute the error with the atom based on the most common pair of items in E
    R_next = [get_best_representation(E[ind], [Aj_next], verbose=False) for ind in range(len(E))]
    el = PCF(E, [Aj_next], R_next, verbose=False)

    # Iterate until the atom updates stop improving the overall cost
    while el < prev_el:
        # Previous iteration was good so that becomes the new baseline
        prev_el = el
        Aj = deepcopy(Aj_next)

        # Add most common element in remaining unrepresented component of E
        #     Only count Documents that are currently using the atom in their representation
        d = Counter()
        for i, ri in enumerate(R_next):
            if len(ri) > 0:
                d.update(E[i].difference(Aj_next))
        if len(d) > 0:
            Aj_next.add(d.most_common(1)[0][0])

        # Update best representation and compute cost
        R_next = [get_best_representation(E[ind], [Aj_next], verbose=False) for ind in range(len(E))]
        el = PCF(E, [Aj_next], R_next, verbose=False)

    if Aj is None:
        print 'No atom created'
    return Aj

def get_error(D, A, R, a_index_to_ignore):
    '''
    Compute the elements for each item in di not represented in by the current Atom/Representation (ignoring atoms we
    are supposed to ignore
    '''
    E = []
    for ind in range(len(D)): # For each Di
        representation_for_item_i = set()
        for atom_index in R[ind]: # Add the elements of this atom to our total set
            if atom_index not in a_index_to_ignore: # If this isn't the atom we are ignoring
                representation_for_item_i.update(A[atom_index])
        error_for_item_i = D[ind].difference(representation_for_item_i)
        E.append(error_for_item_i)
    return E

def get_error2(D, A, R, a_index_to_ignore):
    '''
    Compute the elements for each item in di not represented in by the current Atom/Representation (ignoring atoms we
    are supposed to ignore
    '''
    E = []
    for ind in range(len(D)): # For each Di
        if len(R[ind].intersection(a_index_to_ignore)) > 0:
            representation_for_item_i = set()
            for atom_index in R[ind]: # Add the elements of this atom to our total set
                if atom_index not in a_index_to_ignore: # If this isn't the atom we are ignoring
                    representation_for_item_i.update(A[atom_index])
            error_for_item_i = D[ind].difference(representation_for_item_i)
            E.append(error_for_item_i)
        else:
            E.append(set())
    return E

def PARIS(D, r_slack, num_iterations=3):
    A = []

    for iteration in range(num_iterations):
        print '==========================='
        print '==STARTING WITH %d ATOMS==='%len(A)
        print '==========================='
        # Representation Stage
        R = [get_best_representation(D[ind], A) for ind in range(len(D))]

        # Update Stage: Iterate through atoms replacing if possible
        for a_index_to_update in range(len(A)-1, -1, -1): # iterate backwards
            a_index_to_ignore = set([a_index_to_update])
            E = get_error2(D, A, R, a_index_to_ignore)
            new_a = design_atom(E)
            if new_a is not None and new_a != A[a_index_to_update]:
                print 'Replacing Atom: Index [%d], Items in Common [%d], Items Different [%d]'%(a_index_to_update,
                        len(A[a_index_to_update].symmetric_difference(new_a)),len(new_a.intersection(A[a_index_to_update])))
                del A[a_index_to_update]
                A.append(new_a)

        # Reduction Phase
        R = [get_best_representation(D[ind], A, verbose=False) for ind in range(len(D))]
        prev_error = PCF(D, A, R)
        next_error = prev_error
        should_stop = False
        while next_error <= prev_error and not should_stop:
            prev_error = next_error
            atom_counts = Counter()
            atom_combo_counts = Counter()
            total_count = 0
            for ri in R:
                atom_counts.update(ri)
                atom_combo_counts.update(combinations(list(ri), 2))
                total_count += len(ri)

            #print atom_combo_counts.most_common()
            should_stop = True
            # Check to see if there are any
            for i in range(len(A)-1, -1, -1): # Increment backwards so indexes don't change
                if atom_counts[i] == 0:
                    print "Removing Atom:", i, A[i]
                    del A[i]
                    should_stop = False

            # check to see for every pair if it occurs more than twice it's likelihood
            atoms_to_join = []
            for ((a1, a2), count) in atom_combo_counts.items():
                joint_likelihood_if_indepenent = atom_counts[a1] * atom_counts[a2] /total_count/total_count
                actual_prob = count/total_count
                if actual_prob > 2.0 * joint_likelihood_if_indepenent:
                    atoms_to_join.append((a1,a2))

            if len(atoms_to_join) > 0:
                print 'Atoms that should be joined:', atoms_to_join

            # Check for atoms that have a mostly overlapping set of items
            for (a1, a2) in combinations(range(len(A)), 2):
                if len(A[a1].intersection(A[a2])) > .9*r*max(len(A[a1]), len(A[a2])):
                    atoms_to_join.append((a1, a2))
            if len(atoms_to_join) > 0:
                print 'Atoms that should be joined:', atoms_to_join

            R = [get_best_representation(D[ind], A, verbose=False) for ind in range(len(D))]
            next_error = PCF(D, A, R)



        # Create new atoms
        new_atom = -1
        prev_error = PCF(D, A, R, verbose=False)
        new_error = None
        R_next = R
        while (new_error is None or new_error < prev_error) and new_atom is not None:

            E = get_error(D, A, R_next, set())
            new_atom = design_atom(E) # Don't skip any atoms
            if new_atom is not None:
                A_next = deepcopy(A)
                A_next.append(new_atom)
                R_next = [get_best_representation(D[ind], A_next, verbose=False) for ind in range(len(D))]
                new_error = PCF(D, A_next, R_next, verbose=False)

                if new_error < prev_error:
                    A = A_next
                    R = R_next
                    prev_error = new_error
                    new_error = None
                    print 'Adding Atom: ',  new_error, prev_error, new_atom
                else:
                    print 'Not Adding atom:', new_error, prev_error, new_atom
        print new_error, prev_error, new_atom
        print 'ALL ATOMS: ', A

    print 'Num ATOMS: ', len(A)
    return A, R

def run_paris_on_document(log_file, window_size=20.0, line_count_limit=None, groups_to_skip=set([-1])):

    transactions = defaultdict(set)
    lookup_table = {}
    line_count = 0
    # Iterate through lines building up a lookup table to map Group to template and to build up transactions
    for line in open(log_file):
        if line_count_limit and line_count < line_count_limit:
            line = line.strip().split(',')

            # Extract fileds
            time = float(line[0])
            group = int(line[1])
            if group not in lookup_table:
                # Add to lookup table if we haven't seen this group before for displaying the results
                template = ','.join(line[2:])
                lookup_table[group] = template

            # Based on window add to transactions
            if group not in groups_to_skip:
                window = int(time/window_size)
                transactions[window].add(group)
                # TODO: Allow for overlap here
                line_count +=1

    # PARIS expects a list of sets and not a dictionary, pull values
    D = transactions.values()
    # Run the PARIS algorithm
    A, R = PARIS(D, r_slack)

    # Display the results
    for a in A:
        for group in a:
            print group, lookup_table[group]
        print '--------------------------------------'

def test_with_syntheticdata():
    # Generate synthetic data
    # Define our atoms
    random.seed(1024)
    K = [] # True Atoms
    for i in range(num_K):
        K.append(set(random.sample(range(alphabet_size), num_elements_per_atom)))

    # Generate Input Sets
    D = []
    D_truth= []
    for i in range(N):
        di = set()
        di_truth = set()
        for j in random.sample(range(num_K), L): # Randomly pick L atoms from all atoms
            di_truth.add(j)
            di.update(random.sample(K[j], r_count)) # add r_count items from each atom to our set
        D.append(di)
        D_truth.append(di_truth)

    A, R = PARIS(D, r_slack)

    def get_closest_set(a, K):
        smallest_sym_diff = None
        smallest_k = None
        for k in K:
            sym_diff = a.symmetric_difference(k)
            if smallest_sym_diff is None or sym_diff < smallest_sym_diff:
                smallest_sym_diff = sym_diff
                smallest_k = k
        return smallest_k

    print 'Comparing clusters'
    for a in A:
        print sorted(a), sorted(get_closest_set(a, K))

def main():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", type=str,
                      help="Input log file", metavar="FILE")
    parser.add_option("-w", "--window", dest="window_size", default=20.0, type=float,
                      help="Default window size")
    parser.add_option("-n", "--num_lines", dest="num_lines", default=None, type=int)

    (options, args) = parser.parse_args()
    run_paris_on_document(options.filename, options.window_size, options.num_lines)

if __name__ == "__main__":
    main()