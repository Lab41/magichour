//package ca.pfv.spmf.patterns;

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

import java.text.DecimalFormat;

/**
 * This is an abstract class for an itemset (a set of items.
 *  
 * @see AbstractOrderedItemset
 * @see AbstractMutableOrderedItemset
 * @author Philippe Fournier-Viger
 */
public abstract class AbstractItemset {

	public AbstractItemset() {
		super();
	}

	/**
	 * Get the size of this itemset
	 * @return the size of this itemset
	 */
	public abstract int size();
	
	/**
	 * Get this itemset as a string
	 * @return a string representation of this itemset
	 */
	public abstract String toString();
	
	
	/**
	 * print this itemset to System.out.
	 */
	public void print() {
		System.out.print(toString());
	}
	
	
	/**
	 * Get the support of this itemset
	 * @return the support of this itemset
	 */
	public abstract int getAbsoluteSupport();
	
	/**
	 * Get the relative support of this itemset (a percentage) as a double
	 * @param nbObject  the number of transactions in the database where this itemset was found
	 * @return the relative support of the itemset as a double
	 */
	public abstract double getRelativeSupport(int nbObject);

	/**
	 * Get the relative support of this itemset as a string
	 * @param nbObject  the number of transactions in the database where this itemset was found
	 * @return the relative support of the itemset as a string
	 */
	public String getRelativeSupportAsString(int nbObject) {
		// get the relative support
		double frequence = getRelativeSupport(nbObject);
		// convert it to a string with two decimals
		DecimalFormat format = new DecimalFormat();
		format.setMinimumFractionDigits(0); 
		format.setMaximumFractionDigits(5); 
		return format.format(frequence);
	}
	
	
	/**
	 * Check if this itemset contains a given item.
	 * @param item  the item
	 * @return true if the item is contained in this itemset
	 */
	public abstract boolean contains(Integer item);

}