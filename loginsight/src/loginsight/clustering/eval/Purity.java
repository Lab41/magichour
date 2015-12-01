package loginsight.clustering.eval;

import java.util.List;
import java.util.Set;

import loginsight.core.SimilarityFunction;

public class Purity<C,I> extends ClusterEvaluator<C,I>{
	
	
	public Purity() {
		
	}
	
	public Purity(List insts, SimilarityFunction sim) {
		super(insts, sim);
	}
	
	@Override
	public double eval(int[] centroids, I[] instLabels) {
		Object[] centroidInsts = new Object[centroids.length];
		for (int i=0; i<centroids.length; i++) {
			centroidInsts[i] = _insts.get(centroids[i]);
		}
		Integer[] instCluLabels = new Integer[_insts.size()];
		for (int i=0; i<_insts.size(); i++) {
			Object inst = _insts.get(i);
			double dMaxSim = -Double.MAX_VALUE;
			int cluIndex = -1;
			for (int j=0; j<centroidInsts.length; j++) {
				double sim = _sim.similarity(inst, centroidInsts[j]);
				if (sim >= dMaxSim) {
					dMaxSim = sim;
					cluIndex = j;
				}
			}
			instCluLabels[i] = cluIndex;			
		}		
		return eval_impl(instCluLabels, instLabels);
	}
	
	@Override
	public double eval(C[] instCluLabels, I[] instLabels) {
		// TODO Auto-generated method stub
		return eval(instCluLabels, instLabels);
	}
	
	public static <K,T> double eval_impl(K[] instCluLabels, T[] instLabels) {
		// Build the set of all instance labels		
		Set<Integer>[] instsOfLabels = buildInstsOfLabels(instLabels);
		Set<Integer>[] instsOfCluLabels = buildInstsOfLabels(instCluLabels);
		// Compute the mutual information
		double purity = 0.0;
		for (int i=0; i<instsOfCluLabels.length; i++) {
			Set<Integer> instsSet = instsOfCluLabels[i];
			int maxCommonCount = 0;
			for (int j=0; j<instsOfLabels.length; j++) {
				int count = commonCount(instsSet, instsOfLabels[j]);
				if (count >= maxCommonCount) {
					maxCommonCount = count;
					if (maxCommonCount == instsSet.size()) {
						break;
					}
				}
			}
			purity += maxCommonCount;			
		}
		purity /= instLabels.length;
		return purity;
	}

}
