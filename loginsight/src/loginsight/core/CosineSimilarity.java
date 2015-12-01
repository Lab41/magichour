package loginsight.core;

import loginsight.clustering.SparseVector;

public class CosineSimilarity implements SimilarityFunction {

	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		SparseVector v1 = (SparseVector)o1;
		SparseVector v2 = (SparseVector)o2;			
		return v1.dotProduct(v2);
	}

}
