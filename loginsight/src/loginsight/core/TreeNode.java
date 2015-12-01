package loginsight.core;

import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;


public abstract class TreeNode implements XMLPersistent{
	
	protected List<TreeNode> _children = null;
	protected int _depth = 0;
	protected boolean _isSlot = false;
	protected int[] _instIndices = null;
	protected boolean _canShortDispaly = true; //  For tree visualization
	protected Object _reserved = null;
	
	public TreeNode() {
		
	}
	
	public TreeNode(List<TreeNode> children) {
		addChildren(children);
	}
	
	public void addChild(TreeNode child) {
		if (_children == null) {
			_children = new ArrayList<TreeNode>();
		}
		_children.add(child);
	}
	
	public void addChildren(List<? extends TreeNode> children) {
		if (_children == null) {
			_children = new ArrayList<TreeNode>();
		}
		_children.addAll(children);
	}
	
	public int getChildrenCount() {
		if (_children == null)
			return 0;
		else
			return _children.size();
	}
	
	public boolean hasChild() {
		return getChildrenCount() > 0;
	}
	
	public TreeNode getChild(int index) {
		return _children.get(index);
	}
	
	public List<TreeNode> getChildren() {
		return new ArrayList<TreeNode>(_children);
	}
	
	public Set<TreeNode> getChildrenSet() {
		if (_children != null)
			return new HashSet<TreeNode>(_children);
		else
			return new HashSet<TreeNode>();
	}
	
	public int getDepth() {
		return _depth;
	}
	
	public boolean isSlotNode() {
		return _isSlot;
	}
	
	public void setReserved(Object val) {
		_reserved = val;
	}
	
	public Object getReserved() {
		return _reserved;
	}
	
	public void setIsSlotNode(boolean isSlot) {
		_isSlot = isSlot;
	}
	
	public int[] getInstIndices() {
		return _instIndices;
	}
	
	public void setInstIndices(int[] indices) {
		if (indices == null) {
			_instIndices = null;
		}
		else {
			_instIndices = new int[indices.length];
			System.arraycopy(indices, 0, _instIndices, 0, indices.length);
		}
	}
	
	public void setCanShortDisplay(boolean canShortDisp) {
		_canShortDispaly = canShortDisp;
	}
	
	public boolean canShortDisplay() {
		return _canShortDispaly;
	}
	
	@Override
	public String toString() {
		if (isSlotNode()) {
			return "slot";
		}
		else {
			return getContent().toString();
		}
	}
	
	@Override
	public boolean equals(Object copy) {
		if (!(copy instanceof TreeNode))
			return false;
		TreeNode eCopy = (TreeNode)copy;
		if (this.getContent().equals(eCopy.getContent()) == false)
			return false;
		if (_isSlot != eCopy._isSlot)
			return false;
		return true;
	}
	
	public void print(PrintStream out) {
		for (int i=0; i<_depth; i++) {
			out.print("  ");
		}
		String trimStr = toString();
		trimStr = trimStr.replace('\n', ' ');
		out.println(trimStr);
		if (hasChild()) {
			for (int i=0; i<getChildrenCount(); i++) {
				getChild(i).print(out);
			}
		}
	}
	
	public void getAllNodes(List<TreeNode> nodeList) {
		nodeList.add(this);
		if (!hasChild()) {
			return;
		}
		else {
			for (int i=0; i<getChildrenCount(); i++) {
				getChild(i).getAllNodes(nodeList);
			}
		}
	}
	
	public void getSubNodes(List<TreeNode> nodeList, int depth) {
		if (depth == _depth) {
			nodeList.add(this);
		}
		else if (depth > _depth) {
			if (hasChild()) {
				for (int i=0; i<getChildrenCount(); i++) {
					getChild(i).getSubNodes(nodeList, depth);
				}
			}
		}
	}
	
	/**
	 * Get the number of sub-elements, including itself. 
	 * @return
	 */
	public int getSubNodeCount(boolean bIncludeSlot) {
		if (hasChild()) {
			int count = 1;
			if (bIncludeSlot == false && this.isSlotNode()) {
					count = 0;
			}
			for (int i=0; i<getChildrenCount(); i++) {
				count += getChild(i).getSubNodeCount(bIncludeSlot);
			}
			return count;
		}
		else {
			if (bIncludeSlot == false && this.isSlotNode()) 
				return 0;
			else
				return 1;
		}
	}
	
	public int size(boolean bIncludeSlot) {
		return getSubNodeCount(bIncludeSlot);
	}
	
	public int getMaxDepth() {
		int maxDepth = 0;
		if (hasChild()) {
			for (int i=0; i<getChildrenCount(); i++) {
				int depth = getChild(i).getMaxDepth();
				maxDepth = maxDepth < depth+1 ? depth+1: maxDepth;
			}
		}
		return maxDepth;
	}
	
	public void updateDepth(int rootDepth) {
		_depth = rootDepth;
		if (_children != null) {
			for (int i=0; i<_children.size(); i++) {
				_children.get(i).updateDepth(rootDepth+1);
			}
		}
	}
	
	public abstract Object getContent();
	
	public abstract TreeNode shallowCopy(); 
	
	public abstract TreeNode deepCopy();
	
	public abstract TreeNode createEmptyNode();

}
