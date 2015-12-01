package loginsight.core;

public class StringMatchSimilarity implements SimilarityFunction {

	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		String s1 = (String)o1;
		String s2 = (String)o2;
		String[] words1 = s1.split("\\s");
		String[] words2 = s2.split("\\s");
		int len1 = words1.length;
		int len2 = words2.length;
		int length = Math.min(len1, len2);
		int matchNum = 0;
		for (int i = 0; i<length; i++) {
			if (words1[i].equals(words2[i])) 
				matchNum++;
		}
		return (matchNum) / Math.sqrt(len1*len2);		
	}

}
