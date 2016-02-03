//package patterns;

/* This file is copyright (c) 2008-2012 Philippe Fournier-Viger
* 
* This file is part of the SPMF DATA MINING SOFTWARE
* (http://www.philippe-fournier-viger.com/spmf).
* 
* SPMF is free software: you can redistribute it and/or modify it under the
* terms of the GNU General Public License as published by the Free Software
* Foundation, either version 3 of the License, or (at your option) any later
* version.
* SPMF is distributed in the hope that it will be useful, but WITHOUT ANY
* WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
* A PARTICULAR PURPOSE. See the GNU General Public License for more details.
* You should have received a copy of the GNU General Public License along with
* SPMF. If not, see <http://www.gnu.org/licenses/>.
*/


/**
 * This is an abstract class indicating general methods 
 * that an ordered itemset should have, and is designed for ordered itemsets where items are sorted
 * by lexical order and no item can appear twice.
* 
*  @see AbstractItemset
 * @author Philippe Fournier-Viger
 */
public abstract class AbstractOrderedItemset extends AbstractItemset{

	public AbstractOrderedItemset() {
		super();
	}
	
	/**
	 * Get the support of this itemset
	 * @return the support of this itemset
	 */
	public abstract int getAbsoluteSupport();
	
	/**
	 * Get the size of this itemset
	 * @return the size of this itemset
	 */
	public abstract int size();
	
	/**
	 * Get the item at a given position of this itemset
	 * @param position the position of the item to be returned
	 * @return the item
	 */
	public abstract Integer get(int position);

	/**
	 * Get the last item.
	 * @return the last item.
	 */
	public Integer getLastItem() {
		return get(size() - 1);
	}
	
	/**
	 * Get this itemset as a string
	 * @return a string representation of this itemset
	 */
	public String toString(){
		if(size() == 0) {
			return "EMPTYSET";
		}
		// use a string buffer for more efficiency
		StringBuilder r = new StringBuilder ();
		// for each item, append it to the StringBuilder
		for(int i=0; i< size(); i++){
			r.append(get(i));
			r.append(' ');
		}
		return r.toString(); // return the tring
	}

	
	/**
	 * Get the relative support of this itemset (a percentage) as a double
	 * @param nbObject  the number of transactions in the database where this itemset was found
	 * @return the relative support of the itemset as a double
	 */
	public double getRelativeSupport(int nbObject) {
		// Divide the absolute support by the number of transactions to get the relative support
		return ((double)getAbsoluteSupport()) / ((double) nbObject);
	}

	
	/**
	 * Check if this itemset contains a given item.
	 * @param item  the item
	 * @return true if the item is contained in this itemset
	 */
	public boolean contains(Integer item) {
		for (int i=0; i< size(); i++) {
			if (get(i).equals(item)) {
				return true;
			} else if (get(i) > item) {
				return false;
			}
		}
		return false;
	}
	
	/**
	 * This methods checks if another itemset is contained in this one.
	 * The method assumed that items are lexically ordered in itemsets.
	 * 
	 * @param itemset2 the other itemset
	 * @return true if it is contained
	 */
	/**
	 * This methods checks if another itemset is contained in this one.
	 * @param itemset2 the other itemset
	 * @return true if it is contained
	 */
	public boolean containsAll(AbstractOrderedItemset itemset2){
		// first we check the size
		if(size() < itemset2.size()){
			return false;
		}
		
		// we will use this variable to remember where we are in this itemset
		int i = 0;
		
		// for each item in itemset2, we will try to find it in this itemset
		for(int j =0; j < itemset2.size(); j++){
			boolean found = false; // flag to remember if we have find the item at position j
			
			// we search in this itemset starting from the current position i
			while(found == false && i< size()){
				// if we found the current item from itemset2, we stop searching
				if(get(i).equals(itemset2.get(j))){
					found = true;
				}// if the current item in this itemset is larger than 
				// the current item from itemset2, we return false
				// because the itemsets are assumed to be lexically ordered.
				else if(get(i) > itemset2.get(j)){
					return false;
				}
				
				i++; // continue searching from position  i++
			}
			// if the item was not found in the previous loop, return false
			if(!found){
				return false;
			}
		}
		return true; // if all items were found, return true
	}
	
	/**
	 * This method compare this itemset with another itemset to see if they are
	 * equal. The method assume that the two itemsets are lexically ordered.
	 * @param itemset2 an itemset
	 * @return true or false
	 */
	public boolean isEqualTo(AbstractOrderedItemset itemset2) {
		// If they don't contain the same number of items, we return false
		if (this.size() != itemset2.size()) {
			return false;
		}
		// We compare each item one by one from i to size - 1.
		for (int i = 0; i < itemset2.size(); i++) {
			// if different, return false
			if (!itemset2.get(i).equals(this.get(i))) {
				return false;
			}
		}
		// All the items are the same, we return true.
		return true;
	}
	
	/**
	 * This method compare this itemset with another itemset to see if they are
	 * equal. The method assume that the two itemsets are lexically ordered.
	 * @param an itemset
	 * @return true or false
	 */
	public boolean isEqualTo(int[] itemset) {
		// If they don't contain the same number of items, we return false
		if (this.size() != itemset.length) {
			return false;
		}
		// We compare each item one by one from i to size - 1.
		for (int i = 0; i < itemset.length; i++) {
			// if different, return false
			if (itemset[i] != this.get(i)) {
				return false;
			}
		}
		// All the items are the same, we return true.
		return true;
	}
	
	/**
	 * This method checks if this itemset is the same as another itemset
	 * except for the last item.
	 * @param itemset2 the second itemset
	 * @return true if they are the same except for the last item
	 */
	public boolean allTheSameExceptLastItemV2(AbstractOrderedItemset itemset2) {
		// if they don't contain the same number of item, return false
		if (itemset2.size() != this.size()) {
			return false;
		}
		// Otherwise, we have to compare item by item
		for (int i = 0; i < this.size() - 1; i++) {
			// if they are not the last items, they should be the same
			// otherwise return false
			if (!this.get(i).equals(itemset2.get(i))) {
				return false;
			}
		}
		// All items are the same. We return true.
		return true;
	}
	
	
	/** 
	* Check if the items from this itemset are all the same as those of another itemset 
	* except the last item 
	* and that itemset2 is lexically smaller than this itemset. If all these conditions are satisfied,
	* this method return the last item of itemset2. Otherwise it returns null.
	* @return the last item of itemset2, otherwise, null.
	* */
	public Integer allTheSameExceptLastItem(AbstractOrderedItemset itemset2) {
		// if these itemsets do not have the same size,  return null
		if(itemset2.size() != this.size()){
			return null;
		}
		// We will compare all items one by one starting from position i =0 to size -1
		for(int i=0; i< this.size(); i++){
			// if this is the last position
			if(i == this.size()-1){ 
				// We check if the item from this itemset is be smaller (lexical order) 
				// and different from the one of itemset2.
				// If not, return null.
				if(this.get(i) >= itemset2.get(i)){  
					return null;
				}
			}
			// If this is not the last position, we check if items are the same
			else if(!this.get(i).equals(itemset2.get(i))){ 
				// if not, return null
				return null; 
			}
		}
		// otherwise, we return the position of the last item
		return itemset2.get(itemset2.size()-1);
	}
	

}