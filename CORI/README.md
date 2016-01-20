
CORI mines rare correlated itemsets and was downloaded from SPMF open-source data mining library at http://www.philippe-fournier-viger.com/spmf/

Usage:
java AlgoCORI infile minsupport minbond outfile

0 < minsupport, minbond < 1
The bond of an itemset is the number of transactions containing the itemset divided by the number of transactions containing any of its items. A high value means a highly correlated itemset.  
