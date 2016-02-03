package clustering;

import core.EventType;

public class ClusteredLogEventType implements EventType {
	
	String _content;
	
	public ClusteredLogEventType(String content) {
		_content = content;
	}

	public int compareTo(EventType o) {
		// TODO Auto-generated method stub
		if (o instanceof ClusteredLogEventType) {
			ClusteredLogEventType oE = (ClusteredLogEventType)o;
			return _content.compareTo(oE._content);
		}
		else {
			throw new Error(o.getDescription()+" is not this type");
		}
	}

	public String getDescription() {
		// TODO Auto-generated method stub
		return _content;
	}

	public boolean equals(EventType o) {
		// TODO Auto-generated method stub
		assert(o instanceof ClusteredLogEventType);
		ClusteredLogEventType t = (ClusteredLogEventType)o;
		return _content.equals(t._content);
	}
	
	@Override
	public int hashCode() {
		return _content.hashCode();
	}

}
