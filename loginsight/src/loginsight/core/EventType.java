package loginsight.core;

public interface EventType {
	
	String getDescription();
	
	int compareTo(EventType o);
	
	boolean equals(EventType o);
}
