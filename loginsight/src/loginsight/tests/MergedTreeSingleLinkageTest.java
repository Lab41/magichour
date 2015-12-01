package loginsight.tests;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.util.List;

import loginsight.core.TreeNode;
import loginsight.core.TreeSimilarity;
import loginsight.logtree.FastMsgTreeSimilarity;
import loginsight.logtree.LogElemSimilarity;
import loginsight.logtree.LogElement;
import loginsight.logtree.MergedTreeSingleLinkage;
import loginsight.logtree.parser.FileZillaLogParser;
import loginsight.logtree.parser.MySQLLogParser;

public class MergedTreeSingleLinkageTest {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		test3();
	}
	
	public static void test1() {
		try {
			String filename = "mysqlerr.txt";
			MySQLLogParser parser = new MySQLLogParser();
			List<LogElement> logElemList = parser.parse(new BufferedReader(
					new FileReader(filename)),0, -1);
			FileOutputStream out = new FileOutputStream("out.txt");
			PrintStream outPrint = new PrintStream(out);
			for (int i=0; i<logElemList.size(); i++) {
				LogElement e = logElemList.get(i);
				e.updateDepth(0);
				outPrint.print("index: "+i+"\n");
				e.print(outPrint);
			}
			outPrint.println("\n=======Merged Single-Linkage=======\n");
			TreeSimilarity simFunc =  new LogElemSimilarity();
			System.out.println(""+simFunc.similarity(logElemList.get(56), logElemList.get(56)));
			MergedTreeSingleLinkage sl = new MergedTreeSingleLinkage(logElemList, simFunc, 5);
			sl.build();
			System.out.println();
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	public static void test2() {
		try {
			String filename = "mysqlerr.txt";
			MySQLLogParser parser = new MySQLLogParser();
			List<LogElement> logElemList = parser.parse(new BufferedReader(
					new FileReader(filename)));
			FileOutputStream out = new FileOutputStream("out.txt");
			PrintStream outPrint = new PrintStream(out);
			for (int i=0; i<logElemList.size(); i++) {
				LogElement e = logElemList.get(i);
				e.updateDepth(0);
				outPrint.print("index: "+i+"\n");
				e.print(outPrint);
			}
			outPrint.println("\n=======Merged Tree Single-Linkage=======\n");
			TreeSimilarity simFunc =  new LogElemSimilarity();
			System.out.println(""+simFunc.similarity(logElemList.get(56), logElemList.get(56)));
			MergedTreeSingleLinkage sl = new MergedTreeSingleLinkage(logElemList, simFunc, 0.8);
			sl.build();
			TreeNode[] centroids = sl.getClusterCentroids(4);
			LogElement[] logCentroids = new LogElement[centroids.length];
			System.arraycopy(centroids, 0, logCentroids, 0, centroids.length);
			for (int i=0; i<logCentroids.length; i++) {
				LogElement e = logCentroids[i];
				e.updateDepth(0);
				outPrint.print("index: "+i+"\n");
				e.print(outPrint);
				outPrint.println("instIndex: "+e.getInstIndices());
				e.print(System.out);
				outPrint.println();
			}
			System.out.println();
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	public static void test3() {
		try {
			String filename = "filezilla.log";
			FileZillaLogParser parser = new FileZillaLogParser();
			List<LogElement> logElemList = parser.parse(new BufferedReader(
					new FileReader(filename)));
			FileOutputStream out = new FileOutputStream("out_filezilla.txt");
			PrintStream outPrint = new PrintStream(out);
			for (int i=0; i<logElemList.size(); i++) {
				LogElement e = logElemList.get(i);
				e.updateDepth(0);
				outPrint.print("index: "+i+"\n");
				e.print(outPrint);
			}
			
			outPrint.println("\n=======Merged Tree Single-Linkage=======\n");
			TreeSimilarity simFunc =  new FastMsgTreeSimilarity();
			MergedTreeSingleLinkage sl = new MergedTreeSingleLinkage(logElemList, simFunc, 0.8);
			sl.build();
			sl.save("sl.xml");
			
			sl.load("sl.xml");
			
			TreeNode[] centroids = sl.getClusterCentroids(4);
			LogElement[] logCentroids = new LogElement[centroids.length];
			System.arraycopy(centroids, 0, logCentroids, 0, centroids.length);
			for (int i=0; i<logCentroids.length; i++) {
				LogElement e = logCentroids[i];
				e.updateDepth(0);
				outPrint.print("index: "+i+"\n");
				e.print(outPrint);
				outPrint.println("instIndex: "+e.getInstIndices());
				e.print(System.out);
				outPrint.println();
			}
			System.out.println();
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}

}
