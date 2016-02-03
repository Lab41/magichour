package helper;

import java.util.Calendar;
import java.util.StringTokenizer;

import core.JaccardStringSimilarity;
import core.StringMatchSimilarity;

public class StringHelper {
	
	public static String CalenderToString(Calendar c) {
		StringBuffer sb = new StringBuffer();
		sb.append(c.get(Calendar.YEAR)+"-");
		sb.append(c.get(Calendar.MONTH)+"-");
		sb.append(c.get(Calendar.DAY_OF_MONTH)+" ");
		sb.append(c.get(Calendar.HOUR_OF_DAY)+":");
		sb.append(c.get(Calendar.MINUTE)+":");
		sb.append(c.get(Calendar.SECOND));
		return sb.toString();
	}
	
	public static String IntArrayToString(int[] intArray) {
		StringBuffer sb = new StringBuffer();
		for (int i=0; i<intArray.length; i++) {
			sb.append(intArray[i]+" ");
		}
		return sb.toString();
	}
	
	public static int[] StringToIntArray(String str, int num) {
		StringTokenizer st = new StringTokenizer(str);
		int[] indices = new int[num];
		for (int i = 0; i<num; i++) {
			String token = st.nextToken();
			indices[i] = Integer.parseInt(token);
		}
		return indices;
	}
	
	public static String BoolToString(boolean val) {
		return val? "TRUE" : "FALSE";
	}
	
	public static boolean StringToBool(String str) {
		if (str.equalsIgnoreCase("TRUE"))
			return true;
		else
			return false;
	}
	
	public static String cutStringForShort(String str, int length) {
		if (str.length() > length - 3) {
			return str.substring(0, length-3)+"...";
		}
		else {
			return str;
		}
	}
	
	/**
	 * Compute the similarity between two sentences by Jaccard index
	 * @param s1
	 * @param s2
	 * @return
	 */
	public static double stringJaccard(String s1, String s2) {
		return (new JaccardStringSimilarity()).similarity(s1, s2);
	}
	
	/**
	 * Compute the similarity between two sentences by words matching
	 * @param s1
	 * @param s2
	 * @return
	 */
	public static double stringMatch(String s1, String s2) {
		return (new StringMatchSimilarity()).similarity(s1, s2);
	}

}
