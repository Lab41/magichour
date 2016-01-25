// package cori;

/* This file is copyright (c) 2008-2013 Philippe Fournier-Viger
* 
* This file is part of the SPMF DATA MINING SOFTWARE
* (http://www.philippe-fournier-viger.com/spmf).
* 
* SPMF is free software: you can redistribute it and/or modify it under the
* terms of the GNU General Public License as published by the Free Software
* Foundation, either version 3 of the License, or (at your option) any later
* version.
* 
* SPMF is distributed in the hope that it will be useful, but WITHOUT ANY
* WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
* A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with
* SPMF. If not, see <http://www.gnu.org/licenses/>.
*/

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

//import TriangularMatrix;
//import ca.pfv.spmf.input.transaction_database_list_integers.TransactionDatabase;
//import ca.pfv.spmf.tools.MemoryLogger;
 
/**
 * This is an implementation of the CORI algorithm to mine 
 * correlated itemsets. CORI is actually a quite simple extension of ECLAT.
 * However, it is not explained in the paper describing CORI that it extends ECLAT.
 *  
 * CORI was proposed by Bouasker et Yahia (2015).
 * <br/><br/>
 * 
 * See this article for details about CORI:
 * <br/><br/>
 * 
 * Bouasker, S., Yahia, S. B. (2015).
 * Key correlation mining by simultaneous monotone and anti-monotone 
 * constraints checking. Proc. of the 2015 ACM Symposium on Applied Computing (SAC 2015), pp. 851-856.
 * <br/><br/>
 * 
 * This  version  saves the result to a file
 * or keep it into memory if no output path is provided
 * by the user to the runAlgorithm method().
 * 
 * @see TriangularMatrix
 * @see TransactionDatabase
 * @see ItemsetCORI
 * @see ItemsetsCORI
 * @author Philippe Fournier-Viger 2015
 */
public class AlgoCORI {

	/** relative minimum support **/
	private int minsupRelative;  

	/** minimum bond threshold**/
	private double minBond;  
	
	/** the transaction database **/
	protected TransactionDatabase database; 

	/**  start time of the last execution */
	protected long startTimestamp;
	/** end  time of the last execution */
	protected long endTime; 
	
	/** 
	 The  patterns that are found 
	 (if the user want to keep them into memory) */
	protected ItemsetsCORI frequentItemsets;
	/** object to write the output file */
	BufferedWriter writer = null; 
	/** the number of patterns found */
	protected int itemsetCount; 
	
	/** For optimization with a triangular matrix for counting 
	/ itemsets of size 2.  */
	private TriangularMatrix matrix; // the triangular matrix
	
	/**  buffer for storing the current itemset that is mined when performing mining
	  the idea is to always reuse the same buffer to reduce memory usage. */
	final int BUFFERS_SIZE = 2000;
	/** size of the buffer*/
	private int[] itemsetBuffer = null;

	/**
	 * Default constructor
	 */
	public AlgoCORI() {
		
	}


	/**
	 * Run the algorithm.
	 * @param database a transaction database
	 * @param output an output file path for writing the result or if null the result is saved into memory and returned
	 * @param minsupp the minimum support
	 * @param minBond the minbond threshold
	 * @param useTriangularMatrixOptimization if true the triangular matrix optimization will be applied.
	 * @return the result
	 * @throws IOException exception if error while writing the file.
	 */
	public ItemsetsCORI runAlgorithm(String output, TransactionDatabase database, double minsupp,
			double minBond, boolean useTriangularMatrixOptimization) throws IOException {

		// initialize the buffer for storing the current itemset
		itemsetBuffer = new int[BUFFERS_SIZE];
		
		// Reset the tool to assess the maximum memory usage (for statistics)
		MemoryLogger.getInstance().reset();
		
		// if the user want to keep the result into memory
		if(output == null){
			writer = null;
			frequentItemsets =  new ItemsetsCORI("CORRELATED ITEMSETS");
	    }else{ // if the user want to save the result to a file
	    	frequentItemsets = null;
			writer = new BufferedWriter(new FileWriter(output)); 
		}

		// reset the number of itemset found to 0
		itemsetCount = 0;

		this.database = database;
		
		// record the start time
		startTimestamp = System.currentTimeMillis();
		
		// convert from an absolute minsup to a relative minsup by multiplying
		// by the database size
		this.minsupRelative = (int) Math.ceil(minsupp * database.size());
		
		// save the minbond threshold
		this.minBond = minBond;
		
		// (1) First database pass : calculate tidsets of each item.
		// This map will contain the tidset of each item
		// Key: item   Value :  tidset
		final Map<Integer, BitSetSupport> mapItemTIDS = new HashMap<Integer, BitSetSupport>();
		int maxItemId = calculateSupportSingleItems(database,  mapItemTIDS);

		// If the user chose to use the triangular matrix optimization
		// for counting the support of itemsets of size 2.
		if (useTriangularMatrixOptimization) {
			// We create the triangular matrix.
			matrix = new TriangularMatrix(maxItemId + 1);
			// for each transaction, take each itemset of size 2,
			// and update the triangular matrix.
			for (List<Integer> itemset : database.getTransactions()) {
				Object[] array = itemset.toArray();
				// for each item i in the transaction
				for (int i = 0; i < itemset.size(); i++) {
					Integer itemI = (Integer) array[i];
					// compare with each other item j in the same transaction
					for (int j = i + 1; j < itemset.size(); j++) {
						Integer itemJ = (Integer) array[j];
						// update the matrix count by 1 for the pair i, j
						matrix.incrementCount(itemI, itemJ);
					}
				}
			}
		}

		// (2) create the list of single items
		List<Integer> singleItems = new ArrayList<Integer>();
		
		// for each item
		for(Entry<Integer, BitSetSupport> entry : mapItemTIDS.entrySet()) {
			// get the support and tidset of that item
			BitSetSupport tidset = entry.getValue();
			int support = tidset.support;
			int item = entry.getKey();
			// if the item is frequent
//			if(support >= minsupRelative) {
				// add the item to the list of items
				singleItems.add(item);
//				// output the item
//				saveSingleItem(item, support, tidset.bitset);
//			}else{
				// if infrequent, the item is output
				if(support < minsupRelative) {
					saveSingleItem(item, support, tidset.bitset);
				}
//			}
		}
		
		// Sort the list of items by the total order of increasing support.
		// This total order is suggested in the article by Zaki.
		Collections.sort(singleItems, new Comparator<Integer>() {
			@Override
			public int compare(Integer arg0, Integer arg1) {
				return mapItemTIDS.get(arg0).support - mapItemTIDS.get(arg1).support; 
			}}); 

		
		// Now we will combine each pairs of single items to generate equivalence classes
		// of 2-itemsets
		
		// For each frequent item I according to the total order
		for(int i=0; i < singleItems.size(); i++) {
			Integer itemI = singleItems.get(i);
			// We obtain the tidset and support of that item
			BitSetSupport tidsetI = mapItemTIDS.get(itemI);
			
			// We create empty equivalence class for storing all 2-itemsets starting with
			// the item "i".
			// This equivalence class is represented by two structures.
			// The first structure stores the suffix of all 2-itemsets starting with the prefix "i".
			// For example, if itemI = "1" and the equivalence class contains 12, 13, 14, then
			// the structure "equivalenceClassIitems" will only contain  2, 3 and 4 instead of
			// 12, 13 and 14.  The reason for this implementation choice is that it is more
			// memory efficient.
			List<Integer> equivalenceClassIitems = new ArrayList<Integer>();
			// The second structure stores the tidset of each 2-itemset in the equivalence class
			// of the prefix "i"
			List<BitSetSupport> equivalenceClassItidsets = new ArrayList<BitSetSupport>();
			// The third structure stores the bitset of conjunctive support of each 2-itemset 
			// in the equivalence class
			// of the prefix "i"
			List<BitSetSupport> equivalenceClassConjunctiveItidsets = new ArrayList<BitSetSupport>();
			
			// For each item itemJ that is larger than i according to the total order of
			// increasing support.
loopJ:		for(int j=i+1; j < singleItems.size(); j++) {
				int itemJ = singleItems.get(j);
				
				// if the triangular matrix optimization is activated we obtain
				// the support of itemset "ij" in the matrix. This allows to determine
				// directly without performing a join if "ij" is frequent.
				int supportIJ = -1;
				if(useTriangularMatrixOptimization) {
					// check the support of {i,j} according to the triangular matrix
					supportIJ = matrix.getSupportForItems(itemI, itemJ);
				}
				
				// Obtain the tidset of item J and its support.
				BitSetSupport tidsetJ = mapItemTIDS.get(itemJ);
				
				// Calculate the tidset of itemset "IJ" by performing the intersection of 
				// the tidsets of I and the tidset of J.
				BitSetSupport bitsetSupportIJ = null;
				if(useTriangularMatrixOptimization) {
					// If the triangular matrix optimization is used, then
					// we perform the intersection but do not need to calculate the support
					// since it is already known
					bitsetSupportIJ = performANDFirstTime(tidsetI, tidsetJ, supportIJ);
				}else {
					// Otherwise, we perform the intersection and calculate the support
					// by calculating the cardinality of the resulting tidset.
					bitsetSupportIJ = performAND(tidsetI, tidsetJ);
				}
				
				BitSetSupport conjunctiveSupportIJ = null;
				// After that, we add the itemJ to the equivalence class of 2-itemsets
				// starting with the prefix "i". Note that although we only add "j" to the
				// equivalence class, the item "j" 
				// actually represents the itemset "ij" since we keep the prefix "i" for the
				// whole equivalence class.

				// if the itemset{I,J} has a support of at least 1, we need to keep it.
				if(bitsetSupportIJ.support >= 1) {
					// calculate conjunctive support
					conjunctiveSupportIJ = performOR(tidsetI, tidsetJ);
					
				    equivalenceClassIitems.add(itemJ);
				     // We also keep the tidset of "ij".
				    equivalenceClassItidsets.add(bitsetSupportIJ);
				    // we keep the conjunctive support
				    equivalenceClassConjunctiveItidsets.add(conjunctiveSupportIJ);
				}
			}
			// Process all itemsets from the equivalence class of 2-itemsets starting with prefix I 
			// to find larger itemsets if that class has more than 0 itemsets.
			if(equivalenceClassIitems.size()>0) {
				// This is done by a recursive call. Note that we pass
				// item I to that method as the prefix of that equivalence class.
				itemsetBuffer[0] = itemI;
				processEquivalenceClass(itemsetBuffer, 1, equivalenceClassIitems, equivalenceClassItidsets, equivalenceClassConjunctiveItidsets);
			}
		}
		
		// we check the memory usage
		MemoryLogger.getInstance().checkMemory();
		
		// close the output file if the result was saved to a file
		if(writer != null){
			writer.close();
		}
		
		// record the end time for statistics
		endTime = System.currentTimeMillis();

		// Return all frequent itemsets found!
		return frequentItemsets; 
	}


	/**
	 * This method scans the database to calculate the support of each single item
	 * @param database the transaction database
	 * @param mapItemTIDS  a map to store the tidset corresponding to each item
	 * @return the maximum item id appearing in this database
	 */
	int calculateSupportSingleItems(TransactionDatabase database,
			final Map<Integer, BitSetSupport> mapItemTIDS) {
		
		int maxItemId = 0;
		// for each transaction
		for (int i = 0; i < database.size(); i++) {
			// Add the transaction id to the set of all transaction ids
			// for each item in that transaction
			
			// For each item
			for (Integer item : database.getTransactions().get(i)) {
				// Get the current tidset of that item
				BitSetSupport tids = mapItemTIDS.get(item);
				// If none, then we create one
				if(tids == null){
					tids = new BitSetSupport();
					mapItemTIDS.put(item, tids);
					// we remember the largest item seen until now
					if (item > maxItemId) {
						maxItemId = item;
					}
				}
				// we add the current transaction id to the tidset of the item
				tids.bitset.set(i);
				// we increase the support of that item
				tids.support++;
			}
		}
		return maxItemId;
	}

	/**
	 * Perform the intersection of two tidsets for itemsets containing more than one item.
	 * @param tidsetI the first tidset
	 * @param tidsetJ the second tidset
	 * @return the resulting tidset and its support
	 */
	 BitSetSupport performAND(BitSetSupport tidsetI,
			BitSetSupport tidsetJ) {
		// Create the new tidset and perform the logical AND to intersect the tidset
		BitSetSupport bitsetSupportIJ = new BitSetSupport();
		bitsetSupportIJ.bitset = (BitSet)tidsetI.bitset.clone();
		bitsetSupportIJ.bitset.and(tidsetJ.bitset);
		// set the support as the cardinality of the new tidset
		bitsetSupportIJ.support = bitsetSupportIJ.bitset.cardinality();
		// return the new tidset
		return bitsetSupportIJ;
	}

	/**
	 * Perform the OR of two tidsets for itemsets containing more than one item to
	 * calculate the conjunctive support.
	 * @param tidsetI the first tidset
	 * @param tidsetJ the second tidset
	 * @return the resulting tidset and its support
	 */
	 BitSetSupport performOR(BitSetSupport tidsetI,
			BitSetSupport tidsetJ) {
		// Create the new tidset and perform the logical AND to intersect the tidset
		BitSetSupport bitsetSupportIJ = new BitSetSupport();
		bitsetSupportIJ.bitset = (BitSet)tidsetI.bitset.clone();
		bitsetSupportIJ.bitset.or(tidsetJ.bitset);
		// set the support as the cardinality of the new tidset
		bitsetSupportIJ.support = bitsetSupportIJ.bitset.cardinality();
		// return the new tidset
		return bitsetSupportIJ;
	}
	 
	/**
	 * Perform the intersection of two tidsets representing single items.
	 * @param tidsetI the first tidset
	 * @param tidsetJ the second tidset
	 * @param supportIJ the support of the intersection (already known) so it does not need to 
	 *                  be calculated again
	 * @return  the resulting tidset and its support
	 */
	BitSetSupport performANDFirstTime(BitSetSupport tidsetI,
			BitSetSupport tidsetJ, int supportIJ) {
		// Create the new tidset and perform the logical AND to intersect the tidset
		BitSetSupport bitsetSupportIJ = new BitSetSupport();
		bitsetSupportIJ.bitset = (BitSet)tidsetI.bitset.clone();
		bitsetSupportIJ.bitset.and(tidsetJ.bitset);
		// set the support as the support provided as parameter
		bitsetSupportIJ.support = supportIJ;
		// return the new tidset
		return bitsetSupportIJ;
	}

	/**
	 * This method process all itemsets from an equivalence class to generate larger itemsets,
	 * @param prefix  a common prefix to all itemsets of the equivalence class
	 * @param equivalenceClassItems  a list of suffixes of itemsets in the current equivalence class.
	 * @param equivalenceClassTidsets a list of tidsets of itemsets of the current equivalence class.
	 * @param equivalenceClassConjunctiveItidsets the bitsets of conjunctive support for itemsets of the current equivalence class.
	 * @param prefixLength the prefix length
	 * @throws IOException if error while writting the output to file
	 */
	private void processEquivalenceClass(int[] prefix, int prefixLength, List<Integer> equivalenceClassItems,
			List<BitSetSupport> equivalenceClassTidsets, List<BitSetSupport> equivalenceClassConjunctiveItidsets) throws IOException {
		
		// If there is only one itemset in equivalence class
		if(equivalenceClassItems.size() == 1) {
			int itemI = equivalenceClassItems.get(0);
			BitSetSupport tidsetI = equivalenceClassTidsets.get(0);
			// if the item is infrequent, we save it
			// Then, we just save that itemset to the output and stop.
			// To save the itemset we call the method save with the prefix "prefix" and the suffix
			// "itemI".
			if(tidsetI.support < minsupRelative) {

				BitSetSupport conjunctiveI = equivalenceClassConjunctiveItidsets.get(0);

				// calculate bond
				double bondI = ((double)tidsetI.support) /  conjunctiveI.support;
				if(bondI >= minBond) {
					save(prefix, prefixLength, itemI, tidsetI, bondI);
				}
			}
			return;
		}
		
		// If there are only two itemsets in the equivalence class
		if(equivalenceClassItems.size() == 2) {
			// We get the suffix of the first itemset (an item that we will call I)
			int itemI = equivalenceClassItems.get(0);
			BitSetSupport tidsetI = equivalenceClassTidsets.get(0);
			BitSetSupport conjunctiveI = equivalenceClassConjunctiveItidsets.get(0);
			
			// calculate bond
			double bondI = ((double)tidsetI.support) /  conjunctiveI.support;
			
			// If the itemset with I appended is infrequent we save it
			if(tidsetI.support < minsupRelative && bondI >= minBond) {
				save(prefix, prefixLength, itemI, tidsetI, bondI);
			}

			// We get the suffix of the second itemset (an item that we will call J)
			int itemJ = equivalenceClassItems.get(1);
			BitSetSupport tidsetJ = equivalenceClassTidsets.get(1);
			BitSetSupport conjunctiveJ = equivalenceClassConjunctiveItidsets.get(1);
			
			// If the itemset with J appended is infrequent we save it
			if(tidsetJ.support < minsupRelative) {
				// calculate bond
				double bondJ = ((double)tidsetJ.support) /  conjunctiveJ.support;
				if(bondJ >= minBond) {
					save(prefix, prefixLength, itemJ, tidsetJ, bondJ);
				}
			}
			
			// We calculate the tidset of the itemset resulting from the union of
			// the first itemset and the second itemset.
			BitSetSupport bitsetSupportIJ = performAND(tidsetI, tidsetJ);
			// If the itemset is frequent
			if(bitsetSupportIJ.support < minsupRelative) {
				// Append the prefix with I
				int newPrefixLength = prefixLength+1;
				prefix[prefixLength] = itemI;
				
				// calculate the bond

				if(bitsetSupportIJ.support >= 1 && bitsetSupportIJ.support < minsupRelative) {
					BitSetSupport bitsetConjunctiveSupportIJ = performOR(conjunctiveI, conjunctiveJ);
					double bondIJ = ((double)bitsetSupportIJ.support) /  bitsetConjunctiveSupportIJ.support;
					
					// We save the itemset prefix+IJ to the output if its bond is enough
					if(bondIJ >= minBond) {
						save(prefix, newPrefixLength, itemJ, bitsetSupportIJ, bondIJ);
					}
				}
			}
			return;
		}
		
		// THE FOLLOWING OPTIMIZATION IS COMMENTED SINCE IT DOES NOT IMPROVE PERFORMANCE
		// Sort the equivalence class by support
//		insertionSort(equivalenceClassItems, equivalenceClassTidsets);
		
		// The next loop combines each pairs of itemsets of the equivalence class
		// to form larger itemsets
		
		// For each itemset "prefix" + "i"
		for(int i=0; i< equivalenceClassItems.size(); i++) {
			int itemI = equivalenceClassItems.get(i);
			// get the tidset and support of that itemset
			BitSetSupport tidsetI = equivalenceClassTidsets.get(i);
			BitSetSupport conjunctiveI = equivalenceClassConjunctiveItidsets.get(i);

			// save the itemset "prefix + "i" to file if it is rare
			if(tidsetI.support < minsupRelative) {			
				// calculate bond
				double bondI = ((double)tidsetI.support) /  conjunctiveI.support;
				if(bondI >= minBond) {
					save(prefix, prefixLength, itemI, tidsetI, bondI);
				}
			}
			
			// create the empty equivalence class for storing all itemsets of the 
			// equivalence class starting with prefix + i
			List<Integer> equivalenceClassISuffixItems= new ArrayList<Integer>();
			List<BitSetSupport> equivalenceITidsets = new ArrayList<BitSetSupport>();
			List<BitSetSupport> equivalenceConjunctiveITidsets = new ArrayList<BitSetSupport>();
			
			// For each itemset "prefix" + j"
			for(int j=i+1; j < equivalenceClassItems.size(); j++) {
				int itemJ = equivalenceClassItems.get(j);
				
				// Get the tidset and support of the itemset prefix + "j"
				BitSetSupport tidsetJ = equivalenceClassTidsets.get(j);
				BitSetSupport conjunctiveJ = equivalenceClassConjunctiveItidsets.get(j);
				
				// We will now calculate the tidset of the itemset {prefix, i,j}
				// This is done by intersecting the tidset of the itemset prefix+i
				// with the itemset prefix+j
				BitSetSupport bitsetSupportIJ = performAND(tidsetI, tidsetJ);

				BitSetSupport bitsetConjunctiveSupportIJ = performOR(conjunctiveI, conjunctiveJ);
				
				double bondIJ = ((double)bitsetSupportIJ.support) /  bitsetConjunctiveSupportIJ.support;
				
				// If the itemset prefix+i+j is frequent, then we add it to the
				// equivalence class of itemsets having the prefix "prefix"+i 
				// Note actually, we just keep "j" for optimization because all itemsets
				// in the equivalence class of prefix+i will start with prefix+i so it would just
				// waste memory to keep prefix + i for all itemsets.		
				if(bitsetSupportIJ.support >= 1 && bondIJ >= minBond) {
					equivalenceClassISuffixItems.add(itemJ);
					// We also keep the corresponding tidset and support
					equivalenceITidsets.add(bitsetSupportIJ);
					// We also keep the corresponding tidset and support
					equivalenceConjunctiveITidsets.add(bitsetConjunctiveSupportIJ);
				}
			}

			
			// If there is more than an itemset in the equivalence class 
			// then we recursively process that equivalence class to find larger itemsets
			if(equivalenceClassISuffixItems.size() >0) {
				// We create the itemset prefix + i
				prefix[prefixLength] = itemI;
				int newPrefixLength = prefixLength+1;
				
				// Recursive call
				processEquivalenceClass(prefix, newPrefixLength, equivalenceClassISuffixItems, equivalenceITidsets,equivalenceConjunctiveITidsets);
			}
		}
		
		// we check the memory usage
		MemoryLogger.getInstance().checkMemory();
	}

	/**
	 * Save an itemset to disk or memory (depending on what the user chose).
	 * @param prefix the prefix of the itemset to be saved
	 * @param suffixItem  the last item to be appended to the itemset
	 * @param tidset the tidset and support of this itemset 
	 * @param bond the bond of this itemset 
	 * @param prefixLength the prefix length
	 * @throws IOException if an error occurrs when writing to disk.
	 */
	private void save(int[] prefix, int prefixLength, int suffixItem, BitSetSupport tidset, double bond) throws IOException {
		
		// increase the itemset count
		itemsetCount++;
		// if the result should be saved to memory
		if(writer == null){
			// append the prefix with the suffix
			int[] itemsetArray = new int[prefixLength+1];
			System.arraycopy(prefix, 0, itemsetArray, 0, prefixLength);
			itemsetArray[prefixLength] = suffixItem;
			// Create an object "ItemsetCORI" and add it to the set of frequent itemsets
			ItemsetCORI itemset = new ItemsetCORI(itemsetArray);
			itemset.setAbsoluteSupport(tidset.support);
			itemset.bond = bond;
			frequentItemsets.addItemset(itemset, itemset.size());
		}else{
			// if the result should be saved to a file
			// write it to the output file
			StringBuilder buffer = new StringBuilder();
			for(int i=0; i < prefixLength; i++) {
				int item = prefix[i];
				buffer.append(item);
				buffer.append(" ");
			}
			buffer.append(suffixItem);
			// as well as its support
			//buffer.append(" #SUP: ");
			//buffer.append(tidset.support);
			// as well as its bond
			//buffer.append(" #BOND: ");
			//buffer.append(bond);
			writer.write(buffer.toString());
			writer.newLine();
		}
	}
	
	/**
	 * Save an itemset containing a single item to disk or memory (depending on what the user chose).
	 * @param item the item to be saved
	 * @param support the support of the item
	 * @param tidset the tidset of this itemset
	 * @throws IOException if an error occurrs when writing to disk.
	 */
	private void saveSingleItem(int item, int support, BitSet tidset) throws IOException {
		// increase the itemset count
		itemsetCount++;
		// if the result should be saved to memory
		if(writer == null){
			// add it to the set of frequent itemsets
			ItemsetCORI itemset = new ItemsetCORI(new int[] {item});
			itemset.setAbsoluteSupport(support);
			itemset.bond = 1;
			frequentItemsets.addItemset(itemset, itemset.size());
		}else{
			// if the result should be saved to a file
			// write it to the output file
			StringBuilder buffer = new StringBuilder();
			buffer.append(item);
			//buffer.append(" #SUP: ");
			//buffer.append(support);
			//buffer.append(" #BOND: ");
			//buffer.append(1d);
			writer.write(buffer.toString());
			writer.newLine();
		}
	}


	/**
	 * Print statistics about the algorithm execution to System.out.
	 */
	public void printStats() {
		System.out.println("=============  CORI _96r18 - STATS =============");
		long temps = endTime - startTimestamp;
		System.out.println(" Minbond = " + minBond + " Minsup = " + minsupRelative + " transactions");
		System.out.println(" Database transaction count: " + database.size());
		System.out.println(" Rare correlated itemset count : " + itemsetCount);
		System.out.println(" Total time ~ " + temps + " ms");
		System.out.println(" Maximum memory usage : "
				+ MemoryLogger.getInstance().getMaxMemory() + " mb");
		System.out.println("===================================================");
	}

	/**
	 * Get the set of frequent itemsets.
	 * @return the frequent itemsets (ItemsetsCORI).
	 */
	public ItemsetsCORI getItemsets() {
		return frequentItemsets;
	}

	/**
	 * Anonymous inner class to store a bitset and its cardinality
	 * (an itemset's tidset and its support).
	 * Storing the cardinality is useful because the cardinality() method
	 * of a bitset in Java is very expensive, so it should not be called
	 * more than once.
	 */ 
	public class BitSetSupport{
		BitSet bitset = new BitSet();
		int support;
	}
	
	/* Added main function January 2016 to directly kick off CORI runAlgorithm 
	 * @param input the path to an input file containing a transaction database.
	 * @param output the output file path for saving the result (if null, the result 
	 *        will be returned by the method instead of being saved).
	 * @param minsupp the maximum support threshold.
	 * @param minbond the minimum bond threshold.
	 * @return the result if no output file path is provided.
	 */

	public static void main(String[] args) {
	  AlgoCORI MagicHour = new AlgoCORI();
	  TransactionDatabase transactionList = new TransactionDatabase();
	  if (args.length < 4) System.out.println("\nUsage: java AlgoCORI inputfile minsupport minbond outputfile\n 0 < minsupport, minbond < 1\n");
	  else {
	  	try
	  		{
	  	    transactionList.loadFile(args[0]);
	    	MagicHour.runAlgorithm(args[3], transactionList, Double.parseDouble(args[1]), Double.parseDouble(args[2]), false);
	    	MagicHour.printStats();
	  		}	  
	  	catch (IOException ex) 
	  		{
	    	System.out.println("IO Error");
	    	ex.printStackTrace();
	  		}
	  }
	}
}
