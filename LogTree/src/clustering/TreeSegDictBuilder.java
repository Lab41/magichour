package clustering;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import core.LabeledStringMactchSimilairty;
import core.SimilarityFunction;
import core.SymmetricMatrix;
import core.TreeNode;
import logtree.FastMsgTreeSimilarity;

public class TreeSegDictBuilder {

	double _beta = 0.8;
	double _minFreq = 0.00001;
	int maxDepth = 10;
	SimilarityFunction _contentSim = new LabeledStringMactchSimilairty();
	SimilarityFunction _nodeSim = null;
	FastMsgTreeSimilarity _treeSim = null;
	List<? extends TreeNode> _insts = null;
	double[][] _contentSimMatrix = null;
	double[][][] _levelContentSimMatrix = null;
	
	List<Set<Integer>[]> _levels = new ArrayList<Set<Integer>[]>();
	List<double[][]> _levelSimMatrix = new ArrayList<double[][]>();
	
	public TreeSegDictBuilder(List<? extends TreeNode> insts) {
		_insts = insts;
	}
	
	public TreeSegDictBuilder(List<? extends TreeNode> insts, SimilarityFunction contentSim) {
		_insts = insts;
		_contentSim = contentSim;
	}
	
	public TreeSegDictBuilder(List<? extends TreeNode> insts, double beta) {
		_insts = insts;
		_beta = beta;
	}
	
	public TreeSegDictBuilder(List<? extends TreeNode> insts, SimilarityFunction contentSim, double beta) {
		_insts = insts;
		_beta = beta;
		_contentSim = contentSim;
	}
	
	
	
	static class DictEntry{
		public Object content;
		public int occurence;
		public int columnIndex;
		
		public DictEntry(Object c, int occur, int col) {
			this.content = c;
			this.occurence = occur;
			this.columnIndex = col;
		}
		
		@Override
		public String toString() {
			return content.toString();
		}
	}
	
	public SymmetricMatrix build() {
		int[] maxContentIndex = new int[maxDepth];
		Map<Object, Integer>[] levelContentIndiceMaps = new Map[maxDepth];
		List<DictEntry>[] levelContentLists = new List[maxDepth];
		for (int i=0; i<maxDepth; i++) {
			maxContentIndex[i] = 0;
			levelContentIndiceMaps[i] = new HashMap<Object, Integer>();
			levelContentLists[i] = new ArrayList<DictEntry>();
		}
		
		//Map<Object, Integer> contentIndiceMap = new HashMap<Object, Integer>();
		//List<DictEntry> contentList = new ArrayList<DictEntry>();
		List<TreeNode> subNodes = null;
		int totalNodeSize = 0;
		// DJC long start = System.currentTimeMillis();
		for (int i=0; i<_insts.size(); i++) {
			TreeNode t = _insts.get(i);
			subNodes = new ArrayList<TreeNode>();
			t.getAllNodes(subNodes);
			totalNodeSize += subNodes.size();
			for (int j=0; j<subNodes.size(); j++) {
				TreeNode node = subNodes.get(j);
				int level = node.getDepth();
				Object content = node.getContent();
				if (content == null) {
					node.setReserved(null);
				}
				else {
					Integer entryIndex = levelContentIndiceMaps[level].get(content);
					if (entryIndex == null) {
						levelContentIndiceMaps[level].put(content, maxContentIndex[level]);
						DictEntry dictEntry =  new DictEntry(content, 1, maxContentIndex[level]);
						node.setReserved(dictEntry);
						levelContentLists[level].add(dictEntry);
						maxContentIndex[level]++;
					}
					else {
						DictEntry dictEntry = levelContentLists[level].get(entryIndex);
						dictEntry.occurence++;
						node.setReserved(dictEntry);
					}
				}
			}
		}
		
		
		// Remove small occurrence columns
		int minOccur = (int)(totalNodeSize*_minFreq);
		List<DictEntry>[] levelCompactLists = new List[maxDepth];
		_treeSim = new FastMsgTreeSimilarity(_beta);
		_treeSim.setNodeSimMeasure(new TreeNodeSimilairty());
		_levelContentSimMatrix = new double[maxDepth][][];
		int totalContentNum = 0;

		for (int level =0; level<maxDepth; level++) {
			levelCompactLists[level] = new ArrayList<DictEntry>();
			if (minOccur > 0) {
				for (int i=0; i<levelContentLists[level].size(); i++) {
					DictEntry dictEntry = levelContentLists[level].get(i);
					if (dictEntry.occurence >= minOccur) {
						dictEntry.columnIndex = levelCompactLists[level].size();
						levelCompactLists[level].add(dictEntry);
					}
					else {
						dictEntry.columnIndex = -1;
					}
				}
			}
			else {
				levelCompactLists[level] = levelContentLists[level];
			}
			int contentNum = levelCompactLists[level].size();
			totalContentNum += contentNum;
			_levelContentSimMatrix[level] = new double[contentNum][contentNum];
			double[][] simMatrix = _levelContentSimMatrix[level];
			for (int i=0; i<contentNum; i++) {
				DictEntry c1 = levelCompactLists[level].get(i);
				for (int j=i; j<contentNum; j++) {
					DictEntry c2 = levelCompactLists[level].get(j);
					simMatrix[i][j] = _contentSim.similarity(c1.content, c2.content);
					simMatrix[j][i] = simMatrix[i][j];
				}
			}
		}
		
		//DJC long end = System.currentTimeMillis();
		//DJC System.out.println("Building "+ totalContentNum/2 + " x "+ totalContentNum/2 + " MST, time elapsed: "+(end-start)+"ms");
		
		SymmetricMatrix treeSimMatrix = new SymmetricMatrix(_insts.size());
		for (int i=0; i<_insts.size(); i++) {
			TreeNode t1 = _insts.get(i);
			for (int j=i; j<_insts.size(); j++) {
				TreeNode t2 = _insts.get(j);
				treeSimMatrix.set(i, j , _treeSim.similarity(t1, t2));
			}
		}
		
		return treeSimMatrix;
	}
	
	public int computMSDSize() {
		int[] maxContentIndex = new int[maxDepth];
		Map<Object, Integer>[] levelContentIndiceMaps = new Map[maxDepth];
		List<DictEntry>[] levelContentLists = new List[maxDepth];
		for (int i=0; i<maxDepth; i++) {
			maxContentIndex[i] = 0;
			levelContentIndiceMaps[i] = new HashMap<Object, Integer>();
			levelContentLists[i] = new ArrayList<DictEntry>();
		}
		
		//Map<Object, Integer> contentIndiceMap = new HashMap<Object, Integer>();
		//List<DictEntry> contentList = new ArrayList<DictEntry>();
		List<TreeNode> subNodes = null;
		int totalNodeSize = 0;
		for (int i=0; i<_insts.size(); i++) {
			TreeNode t = _insts.get(i);
			subNodes = new ArrayList<TreeNode>();
			t.getAllNodes(subNodes);
			totalNodeSize += subNodes.size();
			for (int j=0; j<subNodes.size(); j++) {
				TreeNode node = subNodes.get(j);
				int level = node.getDepth();
				Object content = node.getContent();
				if (content == null) {
					node.setReserved(null);
				}
				else {
					Integer entryIndex = levelContentIndiceMaps[level].get(content);
					if (entryIndex == null) {
						levelContentIndiceMaps[level].put(content, maxContentIndex[level]);
						DictEntry dictEntry =  new DictEntry(content, 1, maxContentIndex[level]);
						node.setReserved(dictEntry);
						levelContentLists[level].add(dictEntry);
						maxContentIndex[level]++;
					}
					else {
						DictEntry dictEntry = levelContentLists[level].get(entryIndex);
						dictEntry.occurence++;
						node.setReserved(dictEntry);
					}
				}
			}
		}
		
		
		// Remove small occurrence columns
		int minOccur = (int)(totalNodeSize*_minFreq);
		List<DictEntry>[] levelCompactLists = new List[maxDepth];
		int totalContentNum = 0;

		for (int level =0; level<maxDepth; level++) {
			levelCompactLists[level] = new ArrayList<DictEntry>();
			if (minOccur > 0) {
				for (int i=0; i<levelContentLists[level].size(); i++) {
					DictEntry dictEntry = levelContentLists[level].get(i);
					if (dictEntry.occurence >= minOccur) {
						dictEntry.columnIndex = levelCompactLists[level].size();
						levelCompactLists[level].add(dictEntry);
					}
					else {
						dictEntry.columnIndex = -1;
					}
				}
			}
			else {
				levelCompactLists[level] = levelContentLists[level];
			}
			int contentNum = levelCompactLists[level].size();
			totalContentNum += contentNum*contentNum/2;			
		}
		
		return totalContentNum;
	}
	
	class TreeNodeSimilairty implements SimilarityFunction {

		public double similarity(Object o1, Object o2) {
			// TODO Auto-generated method stub
			double score = 0;
			TreeNode t1 = (TreeNode)o1;
			TreeNode t2 = (TreeNode)o2;
			assert(t1.getDepth() == t2.getDepth());
			int level = t1.getDepth();
			DictEntry e1 = (DictEntry)t1.getReserved();
			DictEntry e2 = (DictEntry)t2.getReserved();
			int contentIndex1 = e1.columnIndex;
			int contentIndex2 = e2.columnIndex;
			if (contentIndex1 >= 0 && contentIndex2 >= 0) {
				score = _levelContentSimMatrix[level][contentIndex1][contentIndex2];
			}
			else {
				score = _contentSim.similarity(t1.getContent(), t2.getContent());
			}
			return score;
		}
		
	}
	
}
