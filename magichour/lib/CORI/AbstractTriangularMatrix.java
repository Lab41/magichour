//package ca.pfv.spmf.datastructures.triangularmatrix;

public interface AbstractTriangularMatrix {

	/**
	 * Return a reprensentation of the triangular matrix as a string.
	 */
	public abstract String toString();

	/**
	 * Increment the value at position i,j
	 * @param i a row id
	 * @param j a column id
	 */
	public abstract void incrementCount(int i, int j);

	/**
	 * Get the value stored at a given position
	 * @param i a row id
	 * @param j a column id
	 * @return the value.
	 */
	public abstract int getSupportForItems(int i, int j);

	public abstract void setSupport(Integer i, Integer j, int support);

}