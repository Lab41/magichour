package loginsight.core;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

public class JaccardStringSimilarity implements SimilarityFunction {
	
	final static int SMALL_SIZE = 10;
	HashMap<String, Set<String>> _stringWordSets = new HashMap<String, Set<String>>();

	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		String s1 = (String)o1;
		String s2 = (String)o2;
		if (s1.length() == 0 && s2.length() == 0) {
			return 0;
		}
		int commonWords = 0;
		int totalSize = -1;
		String[] words1 = s1.split("\\s");
		String[] words2 = s2.split("\\s");
		if (words1.length + words2.length < SMALL_SIZE) { // For small number of words
			totalSize = 0;
			// Remove the duplicate words 
			for (int i=0; i<words1.length; i++) {
				if (words1[i] == null)
					continue;
				totalSize++;
				for (int j=i+1; j<words1.length; j++) {
					if (words1[j] == null)
						continue;
					if (words1[i].equals(words1[j])) {
						words1[j] = null;
					}
				}
			}
			
			// Remove the duplicate words
			for (int i=0; i<words2.length; i++) {
				if (words2[i] == null)
					continue;
				totalSize++;
				for (int j=i+1; j<words2.length; j++) {
					if (words2[j] == null)
						continue;
					if (words2[i].equals(words2[j])) {
						words2[j] = null;
					}
				}
			}
			
			// find the common words
			for (int i=0; i<words1.length; i++) {
				if (words1[i] == null)
					continue;
				boolean bFound = false;
				for (int j=0; j<words2.length; j++) {
					if (words2[j] == null)
						continue;
					if (words1[i].equals(words2[j])) {
						bFound = true;
						break;
					}
				}
				if (bFound) {
					commonWords++;
				}
			}
			totalSize -= commonWords;
		}
		else { // For large number of words
			Set<String> words1Set = _stringWordSets.get(s1);
			if (words1Set == null) {
				words1Set = new HashSet<String>();
				
				for (int i=0; i<words1.length; i++) {
					words1Set.add(words1[i]);
				}
				_stringWordSets.put(s1, words1Set);
			}
			Set<String> words2Set = _stringWordSets.get(s2);
			if (words2Set == null) {
				words2Set = new HashSet<String>();
				
				for (int i=0; i<words2.length; i++) {
					words1Set.add(words2[i]);
				}
				_stringWordSets.put(s2, words1Set);
			}
			
			Iterator<String> it = words1Set.iterator();
			while(it.hasNext()) {
				String word = it.next();
				if (words2Set.contains(word)) {
					commonWords++;
				}
			}
			
			totalSize = words1Set.size() + words2Set.size() - commonWords;
		}
		
		double score = ((double)commonWords) / ((double)totalSize); 
		return score;
	}
	
	

}
