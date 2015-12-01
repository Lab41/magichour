package loginsight.clustering.eval;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import loginsight.core.SimilarityFunction;

public abstract class ClusterEvaluator<C,I> {
	protected List _insts = null;
	protected SimilarityFunction _sim = null;
	
	
	public ClusterEvaluator() {
		
	}
	
	public ClusterEvaluator(List insts, SimilarityFunction sim) {
		_insts = insts;
		_sim = sim;
	}
	
	protected static int commonCount(Set<Integer> s1, Set<Integer> s2) {
		Iterator<Integer> it = s1.iterator();
		int common = 0;
		while(it.hasNext()) {
			Integer index = it.next();
			if (s2.contains(index)) {
				common++;
			}
		}
		return common;
	}
	
	protected static <T> Set<Integer>[] buildInstsOfLabels(T[] instLabels) {
		// Build the set of all instance labels
		Set<T> labelSet = new HashSet<T>();
		for (int i=0; i<instLabels.length; i++) {
			labelSet.add(instLabels[i]);
		}
		int labelCount = labelSet.size();
		// Build the map of label with label index
		HashMap<T, Integer> labelSeqMap = new HashMap<T, Integer>();		
		int labelIndex = 0;
		Iterator<T> labelIt = labelSet.iterator();
		while(labelIt.hasNext()) {
			T label = labelIt.next();
			labelSeqMap.put(label, labelIndex);
			labelIndex++;
		}
		// Build the instance sets for all labels
		Set<Integer>[] instsOfLabels = new Set[labelCount];
		for (int i=0; i<instLabels.length; i++) {
			T label  = instLabels[i];
			labelIndex = labelSeqMap.get(label);
			if (instsOfLabels[labelIndex] == null) {
				instsOfLabels[labelIndex] = new HashSet<Integer>();
			}
			instsOfLabels[labelIndex].add(i);	
		}
		return instsOfLabels;
	}
	
	public abstract double eval(int[] centroids, I[] instLabels);
	
	public abstract double eval(C[] instCluLabels, I[] instLabels);
	
}
