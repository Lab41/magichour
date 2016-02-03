import sys
import os
from collections import defaultdict, namedtuple

# From StringMatch/cluster.py
LogGroup = namedtuple('LogEntry', ['ts', 'group'])

def main():
    if len(sys.argv) == 4 and sys.argv[3] == '-s':
        left_fname = sys.argv[1]
        right_fname = sys.argv[2]
    elif len(sys.argv) == 3:
        right_fname = sys.argv[1]
        left_fname = sys.argv[2]
    else:
        print 'USAGE: python make_comparison.py output_file_1.log output_file_2.log'

    left_basename = os.path.basename(left_fname)
    right_basename = os.path.basename(right_fname)
    # Iterate through left file looking at groups that occur, and tracking that for comparison against the right file
    left_dict = {}
    for line in open(left_fname):
        line = line.strip().split(',')
        group = int(line[1])
        left_dict[','.join(line[2:]).strip()] = group

    # Dictionary of dictionaries {left_group:{right_group:count}}
    output_matrix = defaultdict(lambda : defaultdict(int))

    # Iterate through right file, note which group (from each set) the line falls into and increment that count in the
    #    dictionary of dictionaries (output_matrix)
    for line in open(right_fname):
        line = line.strip().split(',')
        group = int(line[1])
        original_line = ','.join(line[2:]).strip()

        # Make group name based on "FNAME_GROUP"
        left_group = '"%s_%d"'%(right_basename.split('_')[0], group)
        right_group = '"%s_%d"'%(left_basename.split('_')[0], left_dict[original_line])

        # Increment count
        output_matrix[left_group][right_group] += 1

    # Output CSV File
    print 'left,right,count' # Header row
    for left_group in output_matrix:
        for right_group in output_matrix[left_group]:
            output_str = ','.join(['%s'%(left_group), '%s'%(right_group), str(output_matrix[left_group][right_group])])
            print output_str

if __name__ == "__main__":
    main()

