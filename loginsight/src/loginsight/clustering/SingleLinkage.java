package loginsight.clustering;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;

import loginsight.core.SimilarityFunction;
import loginsight.core.SymmetricMatrix;
import loginsight.core.XMLPersistent;
import loginsight.logtree.FastMsgTreeSimilarity;
import loginsight.logtree.LogElemSimilarity;
import loginsight.logtree.LogElement;
import loginsight.logtree.parser.FileZillaLogParser;
import loginsight.logtree.parser.MySQLLogParser;

import org.dom4j.Element;


public class SingleLinkage implements XMLPersistent{
	
	private List _insts = null;
	private SimilarityFunction _simFunc = null;
	private SymmetricMatrix _simMatrix = null;
	private ArrayList<_Cluster> _topLevel = null;
	private double[] _levelSim = null;
	private int _curLevel = -1;
	
	private static class _Cluster {
		private _Cluster[] _children = null;
		private int[] _leafDataIndices = null;
		private int _level = -1;
		
		public _Cluster(int dataIndex) {
			_leafDataIndices = new int[1];
			_leafDataIndices[0] = dataIndex;
		}
		
		public _Cluster(_Cluster[] clusters) {
			int indiceCount = 0;
			_children = new _Cluster[clusters.length];
			System.arraycopy(clusters, 0, _children, 0, clusters.length);
			for (int i=0; i<clusters.length; i++) {
				indiceCount += clusters[i].getDataIndices().length;
			}
			_leafDataIndices = new int[indiceCount];
			int pos =0;
			for (int i=0; i<clusters.length; i++) {
				int[] cDataIndices = clusters[i].getDataIndices();
				System.arraycopy(cDataIndices, 0, _leafDataIndices, pos, cDataIndices.length);
				pos += cDataIndices.length;
			}
		}
		
		public void setLevel(int level) {
			_level = level;
		}
		
		public int getLevel(int level) {
			return _level;
		}
		
		public boolean isLeaf() {
			return _leafDataIndices.length == 1;
		}
		
		public int[] getDataIndices() {
			return _leafDataIndices;
		}
		
		public _Cluster[] getChildren() {
			return _children;
		}
		
		public _Cluster[] getSubClusters(int level) {
			ArrayList<_Cluster> cluList = new ArrayList<_Cluster>();
			getSubClusters(cluList, level);
			_Cluster[] clus = new _Cluster[cluList.size()];
			cluList.toArray(clus);
			return clus;
		}
		
		private void getSubClusters(List<_Cluster> cluList, int level) {
			if (_level >= level)
				cluList.add(this);
			else {
				if (_children != null) {
					for (int i = 0; i < _children.length; i++) {
						_Cluster child = _children[i];
						child.getSubClusters(cluList, level);
					}
				}
			}
		}
	}
	
	public SingleLinkage() {
		
	}
	
	public SingleLinkage(List insts, SimilarityFunction simFunc) {
		_insts = insts;
		_simFunc = simFunc;
		_levelSim = new double[_insts.size()];
		for (int i=0; i<_levelSim.length; i++) {
			_levelSim[i] = 0.0;
		}
	}
	
	public void setSimMatrix(SymmetricMatrix simMatrix) {
		_simMatrix = simMatrix;
	}
	
	public int[] getClusterCentroids(int level) {
		_Cluster[] clusters = _topLevel.get(0).getSubClusters(level);
		int[] centerIndices = new int[clusters.length];
		for (int i=0; i<clusters.length; i++) {
			centerIndices[i] = getCentroid(clusters[i]);
		}
		return centerIndices;
	}
	
	@SuppressWarnings("unchecked")
	public <T> void getClusterCentroids(int level, List<T> list) {
		int[] instIndices = getClusterCentroids(level);
		for (int i=0; i<instIndices.length; i++) {
			list.add((T)_insts.get(instIndices[i]));
		}
	}
	
	@SuppressWarnings("unchecked")
	public <T> void getInsts(List<T> list) {
		for (int i=0; i<_insts.size(); i++) {
			list.add((T)_insts.get(i));
		}
	}
	
	public int getClusterId(int instIndex, int[] clusterCentroids) {
		int matchedIndex = -1;
		double dMaxSim = 0;
		for (int i=0; i<clusterCentroids.length; i++) {
			double d = _simMatrix.get(instIndex, clusterCentroids[i]);
			if (d >= dMaxSim) {
				dMaxSim = d;
				matchedIndex = i;
			}
		}
		return matchedIndex;
	}
	
	private int getCentroid(_Cluster c) {
		double dMaxTotalSim = 0;
		int centerIndex = -1;
		int[] instIndices = c.getDataIndices();
		for (int i=0; i<instIndices.length; i++) {
			int instIndex1 = instIndices[i];
			double dSim = 0;
			for (int j=0; j<instIndices.length; j++) {
				int instIndex2 = instIndices[j];
				dSim +=  _simMatrix.get(instIndex1, instIndex2);
			}
			if (dSim >= dMaxTotalSim) {
				dMaxTotalSim = dSim;
				centerIndex = instIndices[i];
			}
		}
		return centerIndex;
	}
	
	public void build() {
		if (_simMatrix == null) {
			long start = System.currentTimeMillis();
			precomputeSimMatrix();
			long end = System.currentTimeMillis();
			System.out.println("building sim matrix in SL : "+(end-start));
		}
		initBottomLevel();
		while(_topLevel.size() > 1) {
			agglomerate();
		}
	}
	
	public void build(int[] instCluLabel, int level) {
		build();
		int[] cluterInsts = getClusterCentroids(level);
		for (int i=0; i<_insts.size(); i++) {
			instCluLabel[i] = getClusterId(i, cluterInsts);
		}
	}
	
	private void initBottomLevel() {
		_topLevel = new ArrayList<_Cluster>(_insts.size());
		_curLevel = _insts.size()-1;
		for (int i=0; i<_insts.size(); i++) {
			_Cluster c = new _Cluster(i);
			c.setLevel(_curLevel);
			_topLevel.add(c);
		}
		_levelSim[_curLevel] = Double.MAX_VALUE;
	}
	
	private void agglomerate() {
		double maxSim = 0;
		int cluIndex1 = -1;
		int cluIndex2 = -1;
		for (int i=0; i<_topLevel.size(); i++) {
			_Cluster c1 = _topLevel.get(i);
			for (int j=i+1; j<_topLevel.size(); j++) {
				_Cluster c2 = _topLevel.get(j);
				double sim = simBetweenClusters(c1,c2);
				if (maxSim <= sim) {
					maxSim = sim;
					cluIndex1 = i;
					cluIndex2 = j;
				}
			}
		}
		_Cluster c1 = _topLevel.get(cluIndex1);
		_Cluster c2 = _topLevel.get(cluIndex2);
		_Cluster mergedCluster = new _Cluster(new _Cluster[]{c1,c2});
		int c1FirstInst = c1.getDataIndices()[0];
		int c2FirstInst = c2.getDataIndices()[0];
		for (int i=0; i<_topLevel.size(); i++) {
			_Cluster c = _topLevel.get(i);
			int firstInst = c.getDataIndices()[0];
			double c_c1 = _simMatrix.get(firstInst, c1FirstInst);
			double c_c2 = _simMatrix.get(firstInst, c2FirstInst);
			double newscore = c_c1 > c_c2 ? c_c1 : c_c2;
			_simMatrix.set(firstInst, c1FirstInst, newscore);
		}
		
		mergedCluster.setLevel(_curLevel-1);
		_topLevel.set(cluIndex1, mergedCluster);
		// Swap the last one with the second cluster
		if (cluIndex2 < _topLevel.size()-1) {
			_Cluster lastOne = _topLevel.get(_topLevel.size()-1);
			_topLevel.set(cluIndex2, lastOne);
		}
		// Remove the last one
		_topLevel.remove(_topLevel.size()-1);
		_curLevel--;
		_levelSim[_curLevel] = maxSim;
	}
	
	private double simBetweenClusters(_Cluster c1, _Cluster c2) {
		int[] c1Indices = c1.getDataIndices();
		int[] c2Indices = c2.getDataIndices();
		return _simMatrix.get(c1Indices[0], c2Indices[0]);
//		double maxSim = 0;
//		for (int i=0; i<c1Indices.length; i++) {
//			for (int j=0; j<c2Indices.length; j++) {
//				double sim = _simMatrix[c1Indices[i]][c2Indices[j]];
//				if (sim >= maxSim) {
//					maxSim = sim;
//				}
//			}
//		}
//		return maxSim;
	}
		
	private void precomputeSimMatrix() {
		_simMatrix = new SymmetricMatrix(_insts.size());
		for (int i=0; i<_insts.size(); i++) {
			Object o1 = _insts.get(i);
			_simMatrix.set(i, i, 1.0);
			for (int j=i+1; j<_insts.size(); j++) {
				Object o2 = _insts.get(j);
				double sim = _simFunc.similarity(o1, o2);
				_simMatrix.set(i, j, sim);
			}
		}
	}

	public void fromDOM(Element e) throws Exception {
		// TODO Auto-generated method stub
		
	}

	public Element toDOM() throws Exception {
		// TODO Auto-generated method stub
		return null;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		test3();
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
		SingleLinkage sl = new SingleLinkage(insts, new DoubleSim());
		sl.build();
		System.out.println();
	}
	
	private static void test2() {
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
			outPrint.println("\n=======Single-Linkage=======\n");
			SimilarityFunction simFunc =  new LogElemSimilarity();
			System.out.println(""+simFunc.similarity(logElemList.get(56), logElemList.get(56)));
			SingleLinkage sl = new SingleLinkage(logElemList, simFunc);
			sl.build();
			System.out.println();
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	private static void test3() {
		try {
			String filename = "filezilla_1K.log";
			FileZillaLogParser parser = new FileZillaLogParser();
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
			outPrint.println("\n=======Single-Linkage=======\n");
			SimilarityFunction simFunc =  new FastMsgTreeSimilarity();
			LogElement s1 = logElemList.get(16);
			LogElement s2 = logElemList.get(998);
			System.out.println(""+simFunc.similarity(s1, s2));
			SingleLinkage sl = new SingleLinkage(logElemList, simFunc);
			sl.build();
			System.out.println();
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}


}
