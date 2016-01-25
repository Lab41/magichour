package core;

import java.util.ArrayList;
import java.util.List;

public class TreeSet {
	private List<TreeNode> _trees = new ArrayList<TreeNode>();
	
	public TreeSet() {
		
	}
	
	public TreeSet(TreeNode[] trees) {
		for (int i=0; i<trees.length; i++) {
			add(trees[i]);
		}
	}
	
	public void add(TreeNode t) {
		_trees.add(t);
	}
	
	public int getNumTrees() {
		return _trees.size();
	}
	
	public TreeNode getTree(int index) {
		return _trees.get(index);
	}
	
	public TreeNode[] getTrees() {
		return (TreeNode[])_trees.toArray();
	}
}
