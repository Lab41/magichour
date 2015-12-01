package loginsight.clustering;

import java.util.Calendar;

import loginsight.core.EventItem;
import loginsight.core.LogMessage;

public class ClusteredLogEvent implements EventItem<ClusteredLogEventType> {
		
	LogMessage _logMsg;
	String _desc;
	ClusteredLogEventType _type;
	
	public ClusteredLogEvent(LogMessage logMsg, String desc, ClusteredLogEventType type) {
		_logMsg = logMsg;
		_type = type;
		_desc = desc;
	}
	
	public Calendar getEndTime() {
		// TODO Auto-generated method stub
		return _logMsg.getEndTime();
	}

	public Calendar getStartTime() {
		// TODO Auto-generated method stub
		return _logMsg.getStartTime();
	}

	public String getDescription() {
		// TODO Auto-generated method stub
		return _desc;
	}

	public ClusteredLogEventType getType() {
		// TODO Auto-generated method stub
		return _type;
	}

}
