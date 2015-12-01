package loginsight.logtree.parser;

import java.io.BufferedReader;
import java.util.List;

import loginsight.logtree.LogElement;

public interface LogTreeParser {
	
	
	List<LogElement> parse(BufferedReader reader, int start, int size) throws Exception;
	
	List<String> parseForPlain(BufferedReader reader, boolean bExcludeTimestamp, int start, int size) throws Exception;
	
	String[] parseLabels(BufferedReader reader, int start, int size) throws Exception;
}
