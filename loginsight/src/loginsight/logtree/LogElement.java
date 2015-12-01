package loginsight.logtree;

import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import loginsight.core.LogMessage;
import loginsight.core.TreeNode;
import loginsight.helper.StringHelper;

import org.dom4j.DocumentFactory;
import org.dom4j.Element;

public class LogElement extends TreeNode implements LogMessage {
	
	private String _content = null;
	private LogElemLabel _label = null;
	private Calendar _timestamp = null;
	
	public LogElement() {
		
	}

	public LogElement(String content, LogElemLabel l) {
		_content = content;
		_label = l;
		_depth = 0;
	}
	
	public LogElement(List<LogElement> children) {
		_content = "";
		_label = LogElemLabel.RECORD;
		_depth = 0;
		addChildren(children);
	}
		
	public void setTimestamp(Calendar timestamp) {
		_timestamp = timestamp;
	}
	
	public Calendar getTimestamp() {
		return _timestamp;
	}

	public LogElemLabel getLabel() {
		return _label;
	}
	
	public void setLabel(LogElemLabel label) {
		_label = label;
	}
	
	public void getSubElems(List<LogElement> elemList, int depth) {
		if (depth == _depth) {
			elemList.add(this);
		}
		else if (depth > _depth) {
			if (hasChild()) {
				for (int i=0; i<getChildrenCount(); i++) {
					((LogElement)getChild(i)).getSubElems(elemList, depth);
				}
			}
		}
	}
	
	public int size() {
		return this.getSubNodeCount(false);
	}
	
	@Override
	public String toString() {
		if (isSlotNode()) {
			return "slot";
		}
		else if (_label == LogElemLabel.EMPTY) {
			return "[]";
		}
		else {
			return getContent().toString();
		}
	}
	
	public void setContent(String content) {
		_content = content;
	}
	
	@Override
	public String getContent() {
		return _content;
	}
	
	public Calendar getEndTime() {
		// TODO Auto-generated method stub
		return getTimestamp();
	}

	public Calendar getStartTime() {
		// TODO Auto-generated method stub
		return getTimestamp();
	}
	
	@Override
	public TreeNode shallowCopy() {
		// TODO Auto-generated method stub
		LogElement copy = new LogElement(_content, _label);
		copy._depth = _depth;
		copy._timestamp = _timestamp;
		if (_instIndices != null)
			copy._instIndices = Arrays.copyOf(_instIndices, _instIndices.length);
		else
			copy._instIndices = null;
		copy._canShortDispaly = _canShortDispaly;
		copy._isSlot = _isSlot;
		return copy;
	}

	@Override
	public TreeNode deepCopy() {
		// TODO Auto-generated method stub
		LogElement copy = (LogElement)shallowCopy();
		if (_children != null) {
			for (int i=0; i<_children.size(); i++) {
				copy.addChild(this.getChild(i).deepCopy());
			}
		}
		else {
			copy._children = null;
		}
		return copy;
	}

	@Override
	public TreeNode createEmptyNode() {
		// TODO Auto-generated method stub
		return new LogElement("", LogElemLabel.EMPTY);
	}

	public void fromDOM(Element e) throws Exception {
		// TODO Auto-generated method stub
		
		// Read the timestamp
		_timestamp = null;
		if (e.element("timestamp") != null) {
			String timestamp = e.elementText("timestamp");
			DateFormat fm = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
			Date date = fm.parse(timestamp);
			_timestamp = Calendar.getInstance();
			_timestamp.setTime(date);
		}
		
		// Read the content
		_content = e.elementText("content");
		
		// Read the instance indices
		Element instE = e.element("instIndices");
		if (instE == null) {
			_instIndices = null;
		}
		else {
			int numIndices = Integer.parseInt(instE.attributeValue("num"));
			_instIndices = StringHelper.StringToIntArray(instE.getText(), numIndices);
		}
		
		// Read the depth
		_depth = Integer.parseInt(e.elementText("depth"));
		
		// Read the mark to indicate it is a slot or not
		_isSlot = StringHelper.StringToBool(e.elementText("isslot"));
		
		// Read the label
		_label = LogElemLabel.fromString(e.elementText("label"));
		
		// Read the children
		List<Element> childElements = e.elements("LogElement");
		_children = new ArrayList<TreeNode>(childElements.size());
		for (int i=0; i<childElements.size(); i++) {
			LogElement logE = new LogElement("", LogElemLabel.UNKNOWN);
			logE.fromDOM(childElements.get(i));
			_children.add(logE);
		}		
	}

	public Element toDOM() throws Exception{
		// TODO Auto-generated method stub
		Element e = DocumentFactory.getInstance().createElement("LogElement");
		// Write the timestamp
		StringBuffer sb = new StringBuffer();
		if (_timestamp != null) {
			e.addElement("timestamp").addText(StringHelper.CalenderToString(_timestamp));
		}
		
		// Write the content
		e.addElement("content").addText(_content);
		
		// Write the instance indices
		if (this._instIndices != null) {
			Element instE = e.addElement("instIndices");
			instE.addText(StringHelper.IntArrayToString(_instIndices));
			instE.addAttribute("num", ""+_instIndices.length);
		}
		
		// Write the depth
		e.addElement("depth").addText(this._depth+"");
		
		// Write the mark to indicate it is a slot or not
		e.addElement("isslot").addText(StringHelper.BoolToString(_isSlot));
		
		// Write the label
		e.addElement("label").addText(this._label.toString());		
		
		// Write the children
		for (int i=0; i<this.getChildrenCount(); i++) {
			e.add(getChild(i).toDOM());
		}
		return e;
	}

	
	


	
	
	
	
}

