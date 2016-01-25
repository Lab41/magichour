package core;

import java.util.Calendar;

public interface EventItem<T extends EventType>  {
	
	T getType();
	
	String getDescription();
	
	Calendar getStartTime();
	
	Calendar getEndTime();
	
}
