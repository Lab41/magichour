package loginsight.clustering;

import loginsight.core.LabeledStringMactchSimilairty;
import loginsight.core.SimilarityFunction;
import loginsight.core.TreeNode;
import loginsight.core.TreeSimilarity;

public class TreeKernelSimilarity implements TreeSimilarity {
	double _lambda = 0.8;
	SimilarityFunction _contentSim = new LabeledStringMactchSimilairty();
	
	public TreeKernelSimilarity() {
		
	}
	
	public TreeKernelSimilarity(double lambda) {
		_lambda = lambda;
	}
	
	public TreeKernelSimilarity(double lambda, SimilarityFunction contentSim) {
		_lambda = lambda;
		_contentSim = contentSim;
	}

	public double similarity(TreeNode t1, TreeNode t2) {
		// TODO Auto-generated method stub
		double score = 0.0;
		Object o1 = t1.getContent();
		Object o2 = t2.getContent();
		if (o1 != null && o2 != null) {
			score += _contentSim.similarity(o1, o2);
		}
		
		double da = Math.pow(_lambda, t1.getChildrenCount());
		double db = Math.pow(_lambda, t2.getChildrenCount());
		for (int i = 0; i<t1.getChildrenCount(); i++) {
			for (int j=0; j<t2.getChildrenCount(); j++) {
				score += similarity(t1.getChild(i), t2.getChild(j))*da*db;
			}
		}
		return score;
	}

	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		return similarity((TreeNode)o1, (TreeNode)o2);
	}

}
