package clustering.eval;


import java.util.List;

import core.SimilarityFunction;

public class FMeasure<C,I> extends ClusterEvaluator<C,I>{
	double _beta = 1.0;
	
	public FMeasure() {
		
	}
	
	public FMeasure(List insts, SimilarityFunction sim, double beta) {
		super(insts, sim);
		_beta = beta;
	}
	
	public double eval(int[] centroids, I[] instLabels, double beta) {
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
		return eval(instCluLabels, instLabels, beta);		
	}
	
	public static <K,T> double eval(K[] instCluLabels, T[] instLabels, double beta) {
		int TP = 0;
		int FN = 0;
		int FP = 0;
		int TN = 0;
		for (int i=0; i<instLabels.length; i++) {
			for (int j=i+1; j<instLabels.length; j++) {
				if (instLabels[i].equals(instLabels[j])) {
					if (instCluLabels[i].equals(instCluLabels[j])) {
						TP++;
					}
					else {
						FN++;
					}
				}
				else {
					if (instCluLabels[i].equals(instCluLabels[j])) {
						FP++;
					}
					else {
						TN++;
					}
				}
			}
		}
		
		double P = ((double)TP)/((double)(TP+FP));
		double R = ((double)TP)/((double)(TP+FN));
		double fscore = ((beta*beta+1)*P*R)/(beta*beta*P+R);
		return fscore;
	}

	@Override
	public double eval(C[] instCluLabels, I[] instLabels) {
		// TODO Auto-generated method stub
		return eval(instCluLabels, instLabels, _beta);
	}

	@Override
	public double eval(int[] centroids, I[] instLabels) {
		// TODO Auto-generated method stub
		return eval(centroids, instLabels, _beta);
	}
	
	
}
