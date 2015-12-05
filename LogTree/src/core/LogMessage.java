package core;

import java.util.Calendar;

public interface LogMessage {
	
	String getContent();
	
	Calendar getStartTime();
	
	Calendar getEndTime();
}
