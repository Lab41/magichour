from __future__ import division
from math import floor
from collections import Counter, defaultdict
from itertools import combinations, islice

from magichour.api.local.util.log import get_logger, log_time


logger = get_logger(__name__)


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

def PCF(D, A, R, tau=50, r_slack=0, verbose=False):
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
            pcfb += float(len(R[ind]))/len(D[ind])
            #pcfb += float(len([w for i in R[ind] for w in A[i]]))/len(D[ind])
    if verbose:
       print 'PCFA:', pcfa
       print 'PCFB:', pcfb

    # PCFC
    pcfc = tau*len(A)

    total_cost = pcfa + pcfb + pcfc
    if verbose:
        print 'PCFC:', tau*len(A)
        print 'TOTAL: ', total_cost
    return total_cost


def get_best_representation(di, A, verbose=False, r_slack=None):
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

    potential_atoms = []
    for i in range(len(A)):
        if len(di.intersection(A[i])) > 0:
            potential_atoms.append(i)

    # Keep adding atoms to the representation until we are unable to improve the result
    while min_atom_ind is not None:
        # Find atom to add to the representation that minimizes total distance
        min_atom_ind = None
        for i in potential_atoms:
            # Only check distance for items where there is some intersection between the line and the atom
            if i not in curr_r: #and len(di.intersection(A[i])) > 0:
                attempted_r = curr_r
                attempted_r.add(i)
                dist = paris_distance(di, A, attempted_r, r_slack) + 1.0/len(di)*len(attempted_r)
                if verbose:
                    print 'Dist, min_dist', dist, min_distance
                if min_distance is None or dist < min_distance:
                    min_distance = dist
                    min_atom_ind = i

                attempted_r.remove(i)

        if min_atom_ind is not None:
            curr_r.add(min_atom_ind)
    return curr_r

def design_atom(E, r_slack=0, tau=1):
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
    prev_el = PCF(E, [Aj], [set() for ind in range(len(E))], r_slack=r_slack, tau=tau) # Empty representation set

    # Compute the error with the atom based on the most common pair of items in E
    R_next = [get_best_representation(E[ind], [Aj_next], verbose=False, r_slack=r_slack) for ind in range(len(E))]
    el = PCF(E, [Aj_next], R_next, r_slack=r_slack, tau=tau)

    # Iterate until the atom updates stop improving the overall cost
    while el < prev_el:
        # Previous iteration was good so that becomes the new baseline
        prev_el = el
        Aj = Aj_next

        # Add most common element in remaining unrepresented component of E
        #     Only count Documents that are currently using the atom in their representation
        d = Counter()
        for i, ri in enumerate(R_next):
            if len(ri) > 0:
                d.update(E[i].difference(Aj_next))
        if len(d) > 0:
            Aj_next.add(d.most_common(1)[0][0])

        # Update best representation and compute cost
        R_next = [get_best_representation(E[ind], [Aj_next], verbose=False, r_slack=r_slack) for ind in range(len(E))]
        el = PCF(E, [Aj_next], R_next, r_slack=r_slack, tau=tau)

    if len(d) > 0:
        Aj_next.remove(d.most_common(1)[0][0])
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

def PARIS(D, r_slack, num_iterations=3, tau=1.0):
    A = []

    for iteration in range(num_iterations):
        logger.info('==STARTING WITH %d ATOMS==='%len(A))
        # Representation Stage
        R = [get_best_representation(D[ind], A, r_slack=r_slack) for ind in range(len(D))]

        # Update Stage: Iterate through atoms replacing if possible
        for a_index_to_update in range(len(A)-1, -1, -1): # iterate backwards
            a_index_to_ignore = set([a_index_to_update])
            E = get_error2(D, A, R, a_index_to_ignore)
            new_a = design_atom(E, r_slack=r_slack, tau=tau)
            if new_a is not None and new_a != A[a_index_to_update]:
                logger.info('Replacing Atom: Index [%d], Items in Common [%d], Items Different [%d]'%(a_index_to_update,
                        len(A[a_index_to_update].symmetric_difference(new_a)),
                        len(new_a.intersection(A[a_index_to_update]))))
                del A[a_index_to_update]
                A.append(new_a)

        # Reduction Phase
        R = [get_best_representation(D[ind], A, verbose=False, r_slack=r_slack) for ind in range(len(D))]
        prev_error = PCF(D, A, R, r_slack=r_slack, tau=tau)
        next_error = prev_error
        should_stop = False
        while len(A) > 0 and next_error <= prev_error and not should_stop:
            logger.info('Starting Reduction Phase with %d Atoms'%len(A))
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
                    logger.info( "Removing Atom: %s %s"%(i, A[i] ))
                    del A[i]
                    should_stop = False

            # check to see for every pair if it occurs more than twice it's likelihood
            atoms_to_join = []
            edited_atoms = set()
            for ((a1, a2), count) in atom_combo_counts.items():
                if a1 not in edited_atoms and a2 not in edited_atoms:
                    joint_likelihood_if_indepenent = atom_counts[a1] * atom_counts[a2] /total_count/total_count
                    actual_prob = count/total_count
                    if actual_prob > 2.0 * joint_likelihood_if_indepenent:
                        atoms_to_join.append((a1,a2))
                        edited_atoms.add(a1)
                        edited_atoms.add(a2)
                        #edited_atoms.update(range(len(A))) # Only allow edit/iteration

            if len(atoms_to_join) > 0:
                logger.info('Atoms that should be joined: %s'%atoms_to_join)

            # Check for atoms that have a mostly overlapping set of items
            if len(atoms_to_join) == 0:
                for (a1, a2) in combinations(range(len(A)), 2):
                    if a1 not in edited_atoms and a2 not in edited_atoms and len(A[a1].intersection(A[a2])) > .9*max(len(A[a1]), len(A[a2])):
                        atoms_to_join.append((a1, a2))
                        edited_atoms.add(a1)
                        edited_atoms.add(a2)
                        #edited_atoms.update(range(len(A)))  # Only allow edit/iteration

                if len(atoms_to_join) > 0:
                    logger.info('Overlapping atoms that should be joined: %s'%atoms_to_join)

            if len(atoms_to_join)>0:
                deleted_atoms = set()
                def get_new_count(a1, deleted_atoms):
                    '''
                    Small helper function to account for deleted atoms
                    '''
                    num_less_than_a1 = len([a for a in deleted_atoms if a < a1])
                    return a1 - num_less_than_a1
                for (a1, a2) in atoms_to_join:
                    # Delete a1
                    a1_updated = get_new_count(a1, deleted_atoms)
                    a_new = A[a1_updated]
                    del A[a1_updated]
                    deleted_atoms.add(a1)

                    # Delete a2
                    a2_updated = get_new_count(a2, deleted_atoms)
                    a_new.update(A[a2_updated])
                    del A[a2_updated]
                    deleted_atoms.add(a2)

                    A.append(a_new)
                    should_stop = False


            R = [get_best_representation(D[ind], A, verbose=False, r_slack=r_slack) for ind in range(len(D))]
            next_error = PCF(D, A, R, r_slack=r_slack, tau=tau)
            logger.info('ERRORS: next(%s) original(%s) Should Stop: %s'%(next_error, prev_error, should_stop))

        # Create new atoms
        new_atom = -1
        prev_error = PCF(D, A, R, r_slack=r_slack, tau=tau)
        new_error = None
        R_next = R
        while (new_error is None or new_error < prev_error) and new_atom is not None:

            E = get_error(D, A, R_next, set())
            new_atom = design_atom(E, r_slack=r_slack, tau=tau) # Don't skip any atoms
            if new_atom is not None:
                A_next = A
                A_next.append(new_atom)
                R_next = [get_best_representation(D[ind], A_next, verbose=False, r_slack=r_slack) for ind in range(len(D))]
                new_error = PCF(D, A_next, R_next, r_slack=r_slack, tau=tau)

                if new_error < prev_error:
                    A = A_next
                    R = R_next
                    logger.info('Adding Atom: %s\t%s\t%s'%(new_error, prev_error, new_atom))
                    prev_error = new_error
                    new_error = None
                else:
                    A = A[:-1]
                    logger.info('Not Adding atom: %s\t%s\t%s'%(new_error, prev_error, new_atom))
        logger.info('End of iteration cost: %s, %s, %s'%(new_error, prev_error, new_atom))

    logger.info('Num ATOMS: %s '%len(A))
    return A, R

def run_paris_on_document(log_file, window_size=20.0, line_count_limit=None, groups_to_skip=set([-1])):
    import gzip

    transactions = defaultdict(set)
    lookup_table = {}
    line_count = 0
    if log_file.endswith('.gz'):
        fIn = gzip.open(log_file)
    else:
        fIn = open(log_file)

    # Iterate through lines building up a lookup table to map Group to template and to build up transactions
    for line in islice(fIn, line_count_limit):
        line = line.strip().split(',')

        # Extract fields
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

    for a in A:
        print ' '.join(map(str, a))

def test_with_syntheticdata():
    import random
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
    run_paris_on_document(options.filename, options.window_size, line_count_limit=options.num_lines)

if __name__ == "__main__":
    main()
