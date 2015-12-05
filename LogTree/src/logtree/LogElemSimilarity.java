package logtree;

import java.util.ArrayList;
import java.util.List;

import core.TreeNode;
import core.TreeSimilarity;
import helper.StringHelper;
import logtree.parser.MySQLLogParser;

public class LogElemSimilarity implements TreeSimilarity {
	
	public LogElemSimilarity() {
		
	}
	

	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		return similarity((TreeNode)o1, (TreeNode)o2);
	}
	
	public double similarity(TreeNode o1, TreeNode o2) {
		if (!(o1 instanceof LogElement) || !(o2 instanceof LogElement)) {
			throw new Error("This object is not of type LogElement");
		}
		
		LogElement e1 = (LogElement)o1;
		LogElement e2 = (LogElement)o2;
		e1.updateDepth(0);
		e2.updateDepth(0);
		int minDepth = Math.min(e1.getMaxDepth(), e2.getMaxDepth());		
		ArrayList<LogElement> elems1 = new ArrayList<LogElement>();
		ArrayList<LogElement> elems2 = new ArrayList<LogElement>();
		double score1 = 0.0;
		double score2 = 0.0;
		int numRemoved1=0;
		int numRemoved2=0;
		for (int depth=1; depth<=minDepth; depth++) {
			elems1.clear();
			elems2.clear();
			e1.getSubElems(elems1, depth);
			e2.getSubElems(elems2, depth);
//			// Remove DATE and TIME
//			numRemoved1 += removeDateAndTimeElems(elems1);
//			numRemoved2 += removeDateAndTimeElems(elems2);
			// Compute the each element's score
			for (int i=0; i<elems1.size(); i++) {
				double s = getBestMatchScore(elems1.get(i), elems2);;
				score1 += s;
				//System.out.println("left"+s);
			}
			for (int i=0; i<elems2.size(); i++) {
				double s = getBestMatchScore(elems2.get(i), elems1);
				score2 += s;
				//System.out.println("right"+s);
			}
		}
		// The count excludes the root element, date and timestamp elements
		int e1count = e1.getSubNodeCount(false)-1-numRemoved1;
		int e2count = e2.getSubNodeCount(false)-1-numRemoved2;
		return (score1/e1count + score2/e2count)/2; 
	}
	
	/**
	 * Remove the elements of Date and Time-stamp
	 * @param elems
	 * @return the number of elements removed
	 */
	private static int removeDateAndTimeElems(List<LogElement> elems) {
		int count = 0;
		for (int i=0; i<elems.size(); i++) {
			LogElement e = elems.get(i);
			if (e.getLabel() == LogElemLabel.DATE || 
					e.getLabel() == LogElemLabel.TIMESTAMP) {
				elems.remove(i);
				i--;
				count++;
			}
		}
		return count;
	}
	
	private static double getBestMatchScore(LogElement src, List<LogElement> dest) {
		String srcContent = src.getContent();
		if (srcContent == null || srcContent.length() == 0)
			return 0.0;
		
		double dMaxScore = 0.0;
		for (int i=0; i<dest.size(); i++) {
			double score = sentenceSim(srcContent, dest.get(i).getContent());
			if (score > dMaxScore) {
				dMaxScore = score;
			}
		}
		return dMaxScore;
	}
	
	
	private static double sentenceSim(String s1, String s2) {
		return (StringHelper.stringJaccard(s1, s2) + 
				StringHelper.stringMatch(s1,s2))/2.0;
	}
	

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		try{
			String str="100403 17:39:09  InnoDB: Started; log sequence number 0 44233";
			MySQLLogParser parser = new MySQLLogParser();
			LogElement e1 = parser.parseRecord(str);
			
			str = "100403 17:39:09  InnoDB: Started; log sequence number 0 44211";
			LogElement e2 = parser.parseRecord(str);
			
			double sim = new LogElemSimilarity().similarity(e1, e2);
			System.out.println(""+sim);
		}catch(Exception e) {
			e.printStackTrace();
		}
	}


}
