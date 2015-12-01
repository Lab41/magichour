package loginsight.logtree;


import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import loginsight.core.DoublePair;
import loginsight.core.LabeledStringMactchSimilairty;
import loginsight.core.SimilarityFunction;
import loginsight.core.TreeNode;
import loginsight.core.TreeSimilarity;

public class FastMsgTreeSimilarity implements TreeSimilarity {
	
	double _beta = 0.8;
	double _alpha = 0.1;
	SimilarityFunction _contentSim = new LabeledStringMactchSimilairty();
	SimilarityFunction _nodeSim = null;
	
	public FastMsgTreeSimilarity() {
		
	}
	
	public FastMsgTreeSimilarity(SimilarityFunction contentSim) {
		_contentSim = contentSim;
	}
	
	public FastMsgTreeSimilarity(double beta) {
		_beta = beta;
	}
	
	public FastMsgTreeSimilarity(SimilarityFunction contentSim, double beta) {
		_beta = beta;
		_contentSim = contentSim;
	}
	
	public void setNodeSimMeasure(SimilarityFunction nodeSim) {
		_nodeSim = nodeSim;
	}
	
	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		return similarity((TreeNode)o1, (TreeNode)o2);
	}
	
	public double similarity(TreeNode t1, TreeNode t2) {
		return (similarityRoot(t1, t2)+similarityRoot(t2, t1))/2;
	}
	
	
	private double similarityRoot(TreeNode t1, TreeNode t2) {
		// For root node
		double score = 0.0;
		double scoreUpperBound = 0.0;
		if (t1.getContent() != null && t2.getContent() != null) {
			if (_nodeSim != null) 
				score += _nodeSim.similarity(t1, t2);
			else
				score += _contentSim.similarity(t1.getContent(), t2.getContent());
			score = _alpha + (1-_alpha)*score;
			scoreUpperBound += 1.0;
		}
		DoublePair scores = similarity(t1, t2, _beta);
		score += scores.getFirst();
		scoreUpperBound += scores.getSecond();
		return score/scoreUpperBound;
	}
	
	private DoublePair similarity(TreeNode t1, TreeNode t2, double weight) {
		// TODO Auto-generated method stub
		double score = 0.0;
		double scoreUpperBound = 0.0;
		
		// For the child nodes
		if (t1.getChildrenCount()>0) {
			Set<TreeNode> childSet2 = null;
			if (t2 != null) {
				childSet2 = t2.getChildrenSet();
			}
			else {
				childSet2 = new HashSet<TreeNode>();
			}
			
			for (int i=0; i<t1.getChildrenCount(); i++) {
				double dMaxScore = 0;
				TreeNode matchedChild2 = null;
				TreeNode child1 = t1.getChild(i);
				if (childSet2.size() > 0) {
					Iterator<TreeNode> childIt2 = childSet2.iterator();
					while(childIt2.hasNext()) {
						TreeNode child2 = childIt2.next();
						double d = 0.0;
						if (child1.getContent() != null && child2.getContent() != null) {
							if (_nodeSim != null)
								d = _nodeSim.similarity(child1, child2);
							else
								d = _contentSim.similarity(child1.getContent(),
										child2.getContent());
							d = _alpha+(1-_alpha)*d;
						}
						if (d >= dMaxScore) {
							dMaxScore = d;
							matchedChild2 = child2;
						}
					}
					childSet2.remove(matchedChild2);
					score+= dMaxScore*weight;
					scoreUpperBound += weight;
					
					DoublePair scores = similarity(child1, matchedChild2, weight * _beta);
					score += scores.getFirst();
					scoreUpperBound += scores.getSecond();
				}
				else {
					scoreUpperBound += weight;
				}
			}
		}
		return new DoublePair(score, scoreUpperBound);
	}
	
//	@Override
//	public double similarity(TreeNode t1, TreeNode t2) {
//		// TODO Auto-generated method stub
//		LogElement e1 = (LogElement)t1;
//		LogElement e2 = (LogElement)t2;
//		int minDepth = Math.min(e1.getMaxDepth(), e2.getMaxDepth());
//		double score1 = 0.0;
//		double score2 = 0.0;
//		for (int depth=0; depth<=minDepth; depth++) {
//			elems1.clear();
//			elems2.clear();
//			e1.getSubElems(elems1, depth);
//			e2.getSubElems(elems2, depth);
//			double levelcoe = Math.pow(_beta, depth+1);
//			// Compute the each element's score
//			for (int i=0; i<elems1.size(); i++) {
//				double s = getBestMatchScore(elems1.get(i), elems2);
//				score1 += s*levelcoe;
//			}
//			for (int i=0; i<elems2.size(); i++) {
//				double s = getBestMatchScore(elems2.get(i), elems1);
//				score2 += s*levelcoe;
//			}
//		}
//		// The count excludes the root element, date and timestamp elements
//		int e1count = e1.getSubNodeCount(false)-1;
//		int e2count = e2.getSubNodeCount(false)-1;
//		return (score1/e1count + score2/e2count)/2; 
//	}

//	@Override
//	public double similarity(TreeNode t1, TreeNode t2) {
//		// TODO Auto-generated method stub
//		LogElement e1 = (LogElement)t1;
//		LogElement e2 = (LogElement)t2;
//		int minDepth = Math.min(e1.getMaxDepth(), e2.getMaxDepth());
//		double score1 = 0.0;
//		double score2 = 0.0;
//		for (int depth=0; depth<=minDepth; depth++) {
//			elems1.clear();
//			elems2.clear();
//			e1.getSubElems(elems1, depth);
//			e2.getSubElems(elems2, depth);
//			// Compute the each element's score
//			for (int i=0; i<elems1.size(); i++) {
//				double s = getBestMatchScore(elems1.get(i), elems2);;
//				score1 += s;
//			}
//			for (int i=0; i<elems2.size(); i++) {
//				double s = getBestMatchScore(elems2.get(i), elems1);
//				score2 += s;
//			}
//		}
//		// The count excludes the root element, date and timestamp elements
//		int e1count = e1.getSubNodeCount(false)-1;
//		int e2count = e2.getSubNodeCount(false)-1;
//		return (score1/e1count + score2/e2count)/2; 
//	}
//	
//	private double getBestMatchScore(LogElement src, List<LogElement> dest) {
//		String srcContent = src.getContent();
//		if (srcContent == null || srcContent.length() == 0)
//			return 0.0;
//		
//		double dMaxScore = 0.0;
//		for (int i=0; i<dest.size(); i++) {
//			double score = sentenceSim(srcContent, dest.get(i).getContent());
//			if (score > dMaxScore) {
//				dMaxScore = score;
//				if (dMaxScore > 1.0 - 0.000000001) {
//					break;
//				}
//			}
//		}
//		return dMaxScore;
//	}
//		
//	private double sentenceSim(String s1, String s2) {
//		return _contentSim.similarity(s1, s2);
//	}
//	
//	

}
