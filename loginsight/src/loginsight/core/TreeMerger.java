package loginsight.core;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

public class TreeMerger {
	
	public TreeMerger() {
		
	}
	
	public static TreeNode build(TreeNode e1, TreeNode e2) {
		return build(new TreeNode[]{e1,e2});
	}
	
	public static TreeNode build(TreeNode[] nodes) {
		Map<Object, List<TreeNode>> nodeMap = null; 
		nodeMap = new HashMap<Object, List<TreeNode>>();
		for (int i=0; i<nodes.length; i++) {
			TreeNode node = nodes[i];
			List<TreeNode> valueList = nodeMap.get(node.getContent());
			if (valueList == null) {
				valueList = new ArrayList<TreeNode>();
			}
			valueList.add(node);
			nodeMap.put(node.getContent(), valueList);
		}
		return build(nodeMap);
	}
	
	private static TreeNode build(Map<Object, List<TreeNode>> nodes) {
		if (nodes.keySet().size() > 1) {
			TreeNode oneNode = null;
			List<TreeNode> children = new ArrayList<TreeNode>();
			Iterator<Object> keyIt = nodes.keySet().iterator();
			while(keyIt.hasNext()) {
				Object nodeContent = keyIt.next();
				List<TreeNode> nodeList = nodes.get(nodeContent);
				// Create the merged node
				TreeNode mergedNode = merge(nodeList);
				oneNode = mergedNode;
				children.add(mergedNode);
			}
			TreeNode ret = oneNode.createEmptyNode();
			ret.addChildren(children);
			ret.setIsSlotNode(true);
			return ret;
		}
		else if (nodes.keySet().size() == 1) {
			Iterator<Object> keyIt = nodes.keySet().iterator();
			Object nodeContent = keyIt.next();
			List<TreeNode> nodeList = nodes.get(nodeContent);
			// Create the merged node
			return merge(nodeList);
		}
		else {
			return null;
		}
	}
	
	private static TreeNode merge(List<TreeNode> nodeList) {
		if (nodeList.size() == 0)
			return null;
		
		// Create the merged node
		TreeNode firstNode = nodeList.get(0);
		TreeNode mergedNode = firstNode.shallowCopy();

		// Compress the all associated node's children to this merged node
		int childNo = 0;
		while(true) {
			// Check if all the nodes are leaves
			boolean isNoMoreChild = true;
			for (int nIndex=0; nIndex < nodeList.size(); nIndex++) {
				TreeNode e = nodeList.get(nIndex);
				if (e.getChildrenCount() >= childNo +1) {
					isNoMoreChild = false;
					break;
				}
			}
			if (isNoMoreChild) {
				break;
			}
			
			Map<Object, List<TreeNode>> childMap = null; 
			childMap = new HashMap<Object, List<TreeNode>>();
			for (int nIndex=0; nIndex <nodeList.size(); nIndex++ ) {
				TreeNode e = nodeList.get(nIndex);
				TreeNode childElem = null;
				if (e.getChildrenCount() < childNo +1) {
					childElem = firstNode.createEmptyNode();
				}
				else {
					childElem = e.getChild(childNo);
				}
				List<TreeNode> valueList = childMap.get(childElem.getContent());
				if (valueList == null) {
					valueList = new ArrayList<TreeNode>();
				}
				valueList.add(childElem);
				childMap.put(childElem.getContent(), valueList);
			}
			if (childMap.size() == 0) {
				break;
			}
			else {
				mergedNode.addChild(build(childMap));
			}
			childNo++;
		}
		return mergedNode;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		
	}

}
