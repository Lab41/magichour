package loginsight.clustering;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Random;

import loginsight.core.SimilarityFunction;
import loginsight.core.SymmetricMatrix;
import loginsight.logtree.LogElemSimilarity;
import loginsight.logtree.LogElement;
import loginsight.logtree.parser.MySQLLogParser;

public class KMedoids {
	private static double _eps = 1E-16;
	private int[] _medoids = null;
	private List _insts = null;
	private int _k;
	private SimilarityFunction _simFunc = null;
	private SymmetricMatrix _simMatrix = null;
	private Random _rand = new Random();
	
	public KMedoids(int k, List insts, SimilarityFunction simFunc) {
		_medoids = new int[k];
		_insts = insts;
		_k = k;
		_simFunc = simFunc;
		
	}
	
	public void setSimMatrix(SymmetricMatrix simMatrix) {
		_simMatrix = simMatrix;
	}
	
	public int[] build() {
		if (_simMatrix == null) {
			precomputeSimMatrix();
		}
		double lastScore = 0;
		double curScore = 0;
		int[] oldMedoids = new int[_k];
		Arrays.fill(oldMedoids, -1);

		initSeeds();
		while(isMedoidsChange(oldMedoids, _medoids)) {
			// System.out.println("lastScore = "+lastScore+" curScore = "+curScore);
			lastScore = curScore;
			System.arraycopy(_medoids, 0, oldMedoids, 0, _k);
			curScore = refine();
		}
		return _medoids;
	}
	
	public void build(int[] instCluLabels) {
		int[] centroids = build();
		for (int i=0; i<_insts.size(); i++) {
			double dMaxSim = -Double.MAX_VALUE;
			int label = -1;
			for (int j=0; j<centroids.length; j++) {
				double sim = _simMatrix.get(i, centroids[j]);
				if (sim >= dMaxSim) {
					dMaxSim = sim;
					label = j;
				}
			}
			instCluLabels[i] = label;
		}
	}
	
	private static boolean isMedoidsChange(int[] oldMedoids, int[] newMedoids) {
		if (oldMedoids.length != newMedoids.length)
			return true;
		boolean found = false;
		for (int i=0; i<oldMedoids.length; i++) {
			int medoid = oldMedoids[i];
			found = false;
			for (int j=0; j<newMedoids.length; j++) {
				if (medoid == newMedoids[j]) {
					found = true;
					break;
				}
			}
			
			if (found == false) {
				return true;
			}
		}
		return false;
	}
	
	private void initSeeds() {
		if (_k > _insts.size()) {
			throw new Error("The number of clusters is larger than data set");
		}
		HashSet<Integer> selectedInsts = new HashSet<Integer>();
		int size = _insts.size();
		for (int i=0; i<_k; i++) {
			int index = _rand.nextInt()%size;
			index = index < 0 ? (index+size) : index;
			if (selectedInsts.contains(index)) {
				i--;
				continue;
			}
			_medoids[i] = index;
			selectedInsts.add(index);
		}
	}
	
	private double refine() {
		double dMaxScore = -1.0;
		for (int i = 0; i < _k; i++) {			
			for (int j = 0; j < _insts.size(); j++) {
				int oldMedoid = _medoids[i];
				// swap
				_medoids[i] = j;
				// compute new score
				double score = computeTotalSimScore();
				if (score < 0) {
					throw new Error("This score obtained is less than 0 : "
							+ score);
				}
				if (score >= dMaxScore) {
					dMaxScore = score;
				} else {
					// swap back
					_medoids[i] = oldMedoid;
				}
			}
		}
		return dMaxScore;
	}
	
	private double computeTotalSimScore() {
		double totalSim = 0.0;
		for (int i=0; i<_insts.size(); i++) {
			double dMaxSim = -1.0;
			for (int j=0; j<_k; j++) {
				double sim = _simMatrix.get(i, _medoids[j]);
				if (sim >= dMaxSim) {
					dMaxSim = sim;
				}
			}
			totalSim += dMaxSim;
		}
		return totalSim;
	}
	
	
	private void precomputeSimMatrix() {
		_simMatrix = new SymmetricMatrix(_insts.size());
		for (int i=0; i<_insts.size(); i++) {
			Object o1 = _insts.get(i);
			for (int j=i; j<_insts.size(); j++) {				
				Object o2 = _insts.get(j);
				double sim = _simFunc.similarity(o1, o2);
				_simMatrix.set(i, j, sim);
			}
		}
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		test1();
	}
	
	private static void test2() {
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
			outPrint.println("\n=======KMedoids=======\n");
			SimilarityFunction simFunc =  new LogElemSimilarity();
			System.out.println(""+simFunc.similarity(logElemList.get(56), logElemList.get(56)));
			KMedoids kmedoids = new KMedoids(10, logElemList, simFunc);
			int[] clus = kmedoids.build();
			for (int i=0; i<clus.length; i++) {
				LogElement cluElem = logElemList.get(clus[i]);
				outPrint.print(" "+clus[i]);
				System.out.print(" "+clus[i]);
				cluElem.print(outPrint);
			}
			System.out.println();
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	private static void test1() {
		class DoubleSim implements SimilarityFunction {

			public double similarity(Object o1, Object o2) {
				// TODO Auto-generated method stub
				Double d1 = (Double)o1;
				Double d2 = (Double)o2;
				return 1.0/(Math.abs(d1-d2)+1);
			}
		}
		ArrayList<Double> insts = new ArrayList<Double>();
		insts.add(1.0);
		insts.add(2.0);
		insts.add(3.0);
		insts.add(180.0);
		insts.add(120.0);
		insts.add(99.0);
		insts.add(150.0);
		KMedoids kmedoids = new KMedoids(3, insts, new DoubleSim());
		int[] clus = kmedoids.build();
		for (int i=0; i<clus.length; i++) {
			System.out.print(" "+clus[i]);
		}
		System.out.println();
	}

}
