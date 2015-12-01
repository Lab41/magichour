package loginsight.logtree;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

import loginsight.core.Pair;
import loginsight.core.TreeMerger;
import loginsight.core.TreeNode;
import loginsight.core.TreeSimilarity;
import loginsight.core.XMLPersistent;

import org.dom4j.Document;
import org.dom4j.DocumentFactory;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;

public class MergedTreeSingleLinkage implements XMLPersistent{
	
	private List<TreeNode> _insts = null;
	private TreeSimilarity _simFunc = null;
	private List<_Cluster> _topLevel = null;
	private double[] _levelSim = null;
	private int _curLevel = -1;
	private double _maxMergeRatio = 0.5;
	private double[][] _simMatrix = null;
	private final static double _simGap = 5.0;
	
	/**
	 * The inner class for cluster
	 * @author Liang
	 *
	 */
	private static class _Cluster implements XMLPersistent {
		private _Cluster[] _children = null;
		private int[] _leafDataIndices = null;
		private int _level = -1;
		private boolean _isSingleTree = true;
		private int _singleTreeSize = -1;
		
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
		
		public boolean isSingleTree() {
			return _isSingleTree;
		}
		
		public void setIsSingleTree(boolean isSingle) {
			_isSingleTree = isSingle;
		}
		
		public int getSingleTreeSize() {
			return _singleTreeSize;
		}
		
		public void setSingleTreeSize(int treeSize) {
			_singleTreeSize = treeSize;
		}
		
		public boolean isLeaf() {
			return _leafDataIndices.length == 1;
		}
		
		public int[] getDataIndices() {
			return _leafDataIndices;
		}
		
		public int getDataIndex() {
			return _leafDataIndices[0];
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

		public void fromDOM(Element e) throws Exception {
			// TODO Auto-generated method stub
			// Read leaf data indices
			String strLeafDataIndices = e.elementText("LeafDataIndices");
			StringTokenizer st = new StringTokenizer(strLeafDataIndices);
			ArrayList<Integer> leafIndices = new ArrayList<Integer>();
			while(st.hasMoreTokens()) {
				String token = st.nextToken();
				leafIndices.add(Integer.parseInt(token));
			}
			_leafDataIndices = new int[leafIndices.size()];
			for (int i=0; i<leafIndices.size(); i++) {
				_leafDataIndices[i] = leafIndices.get(i);
			}
			// Read single tree indicator
			String strIsSingleTree = e.elementText("IsSingleTree");
			_isSingleTree = strIsSingleTree.equalsIgnoreCase("TRUE");
			// Read single tree size
			String strSingleTreeSize = e.elementText("SingleTreeSize");
			_singleTreeSize = Integer.parseInt(strSingleTreeSize);
			// Read level
			String strLevel = e.elementText("Level");
			_level = Integer.parseInt(strLevel);
			// Read children
			List<Element> childElements = e.elements("_Cluster");
			_children = new _Cluster[childElements.size()];
			for (int i=0; i<childElements.size(); i++) {
				_children[i] = new _Cluster(-1);
				_children[i].fromDOM(childElements.get(i));				
			}
		}

		public Element toDOM() throws Exception {
			// TODO Auto-generated method stub
			Element e = DocumentFactory.getInstance().createElement("_Cluster");
			// Write the leaf data indices
			StringBuffer sb = new StringBuffer();
			for (int i=0; i<this._leafDataIndices.length; i++) {
				sb.append(_leafDataIndices[i]+" ");
			}
			e.addElement("LeafDataIndices").addText(sb.toString());
			// Write single tree indicator
			String strIsSingleTree = _isSingleTree ? "TRUE":"FALSE";
			e.addElement("IsSingleTree").addText(strIsSingleTree);
			// Write single tree size
			e.addElement("SingleTreeSize").addText(""+_singleTreeSize);
			// Write level
			e.addElement("Level").addText(""+_level);
			// Write children
			if (_children != null) {
				for (int i=0; i<_children.length; i++) {
					_Cluster c = _children[i];
					e.add(c.toDOM());
				}
			}
			
			return e;
		}
	}
	
	/**
	 * The constructor
	 * @param insts  The input trees
	 * @param simFunc The similarity function of trees
	 * @param maxMergeRatio The maximum size of merged tree
	 */
	public MergedTreeSingleLinkage(List<? extends TreeNode> insts, TreeSimilarity simFunc, 
			double maxMergeRatio) {
		_insts = (List<TreeNode>)insts;
		_simFunc = simFunc;
		_maxMergeRatio = maxMergeRatio;
		_levelSim = new double[_insts.size()];
		for (int i=0; i<_levelSim.length; i++)
			_levelSim[i] = 0.0;
	}
	
	public MergedTreeSingleLinkage() {
		
	}
	
	/**
	 * Build the clusters
	 */
	public void build() {
		precomputeSimMatrix();
		initBottomLevel();
		while(_topLevel.size() > 1) {
			agglomerate();
		}
	}
		
	private void initBottomLevel() {
		_topLevel = new ArrayList<_Cluster>(_insts.size());
		_curLevel = _insts.size()-1;
		for (int i=0; i<_insts.size(); i++) {
			_Cluster c = new _Cluster(i);
			TreeNode t = _insts.get(i);
			c.setIsSingleTree(true);
			c.setSingleTreeSize(t.size(false));
			c.setLevel(_curLevel);
			_topLevel.add(c);
		}
		_levelSim[_curLevel] = Double.MAX_VALUE;
	}
	
	private void agglomerate() {
		double maxSim = 0;
		int mergedTreeSize = -1;
		int cluIndex1 = -1;
		int cluIndex2 = -1;
		// Find the most similar pair of clusters
		for (int i=0; i<_topLevel.size(); i++) {
			_Cluster c1 = _topLevel.get(i);
			for (int j=i+1; j<_topLevel.size(); j++) {
				_Cluster c2 = _topLevel.get(j);
				Pair<Double, Integer> ret = simBetweenClusters(c1,c2);
				double sim = ret.getFirst();
				if (maxSim <= sim) {
					maxSim = sim;
					cluIndex1 = i;
					cluIndex2 = j;
					mergedTreeSize = ret.getSecond();
				}
			}
		}
		// Merge the two clusters
		_Cluster c1 = _topLevel.get(cluIndex1);
		_Cluster c2 = _topLevel.get(cluIndex2);
		_Cluster mergedCluster = new _Cluster(new _Cluster[]{c1,c2});
		mergedCluster.setLevel(_curLevel-1);
		if (maxSim >= _simGap) {
			mergedCluster.setIsSingleTree(true);
			mergedCluster.setSingleTreeSize(mergedTreeSize);
		}
		else {
			mergedCluster.setIsSingleTree(false);
		}
		_topLevel.set(cluIndex1, mergedCluster);
		_topLevel.remove(cluIndex2);
		_curLevel--;
		_levelSim[_curLevel] = maxSim;
	}
	
	private Pair<Double, Integer> simBetweenClusters(_Cluster c1, _Cluster c2) {
		int[] c1Indices = c1.getDataIndices();
		int[] c2Indices = c2.getDataIndices();
		double maxSim = 0;
		int mergedTreeSize = -1;
		// Check if the tree sets can be merged
		boolean bCanMerged = false;
		if (c1.isSingleTree() && c2.isSingleTree()) {
			TreeNode[] treeSet = new TreeNode[c1Indices.length+c2Indices.length];
			int index = 0;
			for (int i=0; i<c1Indices.length; i++) {
				treeSet[index++] = _insts.get(c1Indices[i]);
			}
			for (int i=0; i<c2Indices.length; i++) {
				treeSet[index++] = _insts.get(c2Indices[i]);
			}
			TreeNode mergedTree = TreeMerger.build(treeSet);
			mergedTreeSize = mergedTree.size(false);
			double totalTreeSize = c1.getSingleTreeSize() + c2.getSingleTreeSize();
			double mergeRatio = mergedTreeSize / totalTreeSize;
			if ( mergeRatio <= _maxMergeRatio) {
				bCanMerged = true;
				maxSim = totalTreeSize / (mergedTreeSize);
				maxSim += _simGap;
			}
			else {
				bCanMerged = false;
			}
		}
		
		if (bCanMerged) {
			return new Pair<Double, Integer>(maxSim, mergedTreeSize);
		}
		
		maxSim = 0;
		for (int i=0; i<c1Indices.length; i++) {
			for (int j=0; j<c2Indices.length; j++) {
				double sim = _simMatrix[c1Indices[i]][c2Indices[j]];
				if (sim >= maxSim) {
					maxSim = sim;
				}
			}
		}		
		return new Pair<Double, Integer>(maxSim, mergedTreeSize);
	}
	
	private void precomputeSimMatrix() {
		_simMatrix = new double[_insts.size()][_insts.size()];
		for (int i=0; i<_insts.size(); i++) {
			Object o1 = _insts.get(i);
			_simMatrix[i][i] = 1.0;
			for (int j=i+1; j<_insts.size(); j++) {
				Object o2 = _insts.get(j);
				double sim = _simFunc.similarity(o1, o2);
				_simMatrix[i][j] = sim;
				_simMatrix[j][i] = sim;
			}
		}
	}
	
	public TreeNode[] getClusterCentroids(int level) {
		_Cluster[] clusters = _topLevel.get(0).getSubClusters(level);
		TreeNode[] centroids = new TreeNode[clusters.length];
		for (int i=0; i<clusters.length; i++) {
			_Cluster c = clusters[i];
			 TreeNode t = getCentroidOfCluster(c);
			 centroids[i] = t;
		}
		return centroids;
	}
	
	@SuppressWarnings("unchecked")
	public <T extends TreeNode> void getClusterCentroids(int level, List<T> list) {
		TreeNode[] trees = getClusterCentroids(level);
		for (int i=0; i<trees.length; i++) {
			list.add((T)trees[i]);
		}
	}
	
	@SuppressWarnings("unchecked")
	public <T extends TreeNode> void getInsts(List<T> list) {
		for (int i=0; i<_insts.size(); i++) {
			list.add((T)_insts.get(i));
		}
	}
	
	private TreeNode getCentroidOfCluster(_Cluster c) {
		List<TreeNode> trees = new ArrayList<TreeNode>();
		getTreeNodesOfCluster(trees, c);
		return getCentroid(trees);
	}
	
	private TreeNode getCentroid(List<TreeNode> trees) {
		double dMaxTotalSim = 0;
		TreeNode centroidTree = null;
		for (int i=0; i<trees.size(); i++) {
			TreeNode t1 = trees.get(i);
			double dSim = 0;
			for (int j=0; j<trees.size(); j++) {
				TreeNode t2 = trees.get(j);
				double sim = 0;
				int[] instIndices1 = t1.getInstIndices();
				int[] instIndices2 = t2.getInstIndices();				
				if (instIndices1 != null && instIndices1.length == 1 &&
						instIndices2 != null && instIndices1.length == 2 ) {
					int instIndex1 = instIndices1[0];
					int instIndex2 = instIndices2[0];
					sim = _simMatrix[instIndex1][instIndex2];
				}
				else {
					sim = _simFunc.similarity(t1, t2);
				}
				dSim += sim;
			}
			if (dSim >= dMaxTotalSim) {
				dMaxTotalSim = dSim;
				centroidTree = t1;
			}
		}
		return centroidTree.deepCopy();
	}
	
	private void getTreeNodesOfCluster(List<TreeNode> trees, _Cluster c) {
		if (c.isLeaf()) {
			TreeNode t = _insts.get(c.getDataIndex());
			t.setInstIndices(c.getDataIndices());
			trees.add(t);
		}
		else if (c.isSingleTree()) {
			int[] dataIndices = c.getDataIndices();
			TreeNode[] ttrees = new TreeNode[dataIndices.length];
			for (int i=0; i<dataIndices.length; i++) {
				ttrees[i] = _insts.get(dataIndices[i]);
			}
			TreeNode mergedTree = TreeMerger.build(ttrees);
			mergedTree.setInstIndices(dataIndices); // indicates this tree is a merged tree
			trees.add(mergedTree);
		}
		else {
			_Cluster[] subClusters = c.getChildren();
			for (int i=0; i<subClusters.length; i++) {
				getTreeNodesOfCluster(trees, subClusters[i]);
			}
		}
		
	}
	

	public void fromDOM(Element e) throws Exception {
		// TODO Auto-generated method stub
		// Read data instances
		String instClassName = e.elementText("InstanceClassName");
		Element instsElem = e.element("Instances");
		List<Element> instElems = instsElem.elements();
		_insts = new ArrayList<TreeNode>(instElems.size());
		for (int i=0; i<instElems.size(); i++) {
			TreeNode inst = (TreeNode)Class.forName(instClassName).newInstance();
			inst.fromDOM(instElems.get(i));
			_insts.add(inst);
		}
		// Read the similarity function
		String simClassName = e.elementText("SimilarityClassName");
		_simFunc = (TreeSimilarity)Class.forName(simClassName).newInstance();
		// Read the similarity matrix
		Element simMatrixElem = e.element("SimMatrix");
		List<Element> simElems = simMatrixElem.elements();
		_simMatrix = new double[_insts.size()][_insts.size()];
		for (int i=0; i<simElems.size(); i++) {
			Element simValE = simElems.get(i);
			String strRow = simValE.attributeValue("row");
			String strCol = simValE.attributeValue("col");
			String strVal = simValE.getText();
			int row = Integer.parseInt(strRow);
			int col = Integer.parseInt(strCol);
			double val = Double.parseDouble(strVal);
			_simMatrix[row][col] = val;
		}
		// Read top level clusters
		Element clustersElem = e.element("Clusters");
		List<Element> clusterList = clustersElem.elements();
		_topLevel = new ArrayList<_Cluster>(clusterList.size());
		for (int i=0; i<clusterList.size(); i++) {
			Element cluElem = clusterList.get(i);
			_Cluster c = new _Cluster(-1);
			c.fromDOM(cluElem);
			_topLevel.add(c);
		}		
	}

	public Element toDOM() throws Exception {
		// TODO Auto-generated method stub
		Element e = DocumentFactory.getInstance().createElement("SL");
		// Write the data instances
		String instClassName = _insts.get(0).getClass().getName();
		e.addElement("InstanceClassName").addText(instClassName);
		Element instsElem = e.addElement("Instances");
		for (int i=0; i<_insts.size(); i++) {
			TreeNode inst = _insts.get(i);
			instsElem.add(inst.toDOM());
		}
		// Write similarity function
		String simClassName = _simFunc.getClass().getName();
		e.addElement("SimilarityClassName").addText(simClassName);
		// Write the similarity matrix
		Element simMatrixElem = e.addElement("SimMatrix");
		for (int i=0; i<this._simMatrix.length; i++) {
			double[] arr = this._simMatrix[i];
			for (int j=0; j<arr.length; j++) {
				Element simValE = simMatrixElem.addElement("value");
				simValE.addAttribute("row", ""+i);
				simValE.addAttribute("col", ""+j);
				simValE.addText(""+arr[j]);
			}
		}
		// Write top level clusters
		Element clustersElem = e.addElement("Clusters");
		for (int i=0; i<_topLevel.size(); i++) {
			clustersElem.add(_topLevel.get(i).toDOM());
		}
		
		return e;
	}
	
	public void load(String fileName) throws Exception {
		File xmlFile = new File(fileName);
		SAXReader reader = new SAXReader();
	    Document doc = reader.read(xmlFile);
	    Element root = doc.getRootElement();
	    this.fromDOM((Element)root.elementIterator().next());
	}
	
	public void save(String fileName) throws Exception {
		Document doc = DocumentFactory.getInstance().createDocument();
		Element root = doc.addElement("SL");
		root.add(this.toDOM());
		FileOutputStream fos = new FileOutputStream(fileName);
		OutputFormat format = OutputFormat.createPrettyPrint();
		XMLWriter writer = new XMLWriter(fos, format);
		writer.write(doc);
		writer.close();
	}

	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		loginsight.tests.MergedTreeSingleLinkageTest.main(args);
	}

}
