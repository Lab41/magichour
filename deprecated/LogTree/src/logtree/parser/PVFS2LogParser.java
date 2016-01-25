package logtree.parser;

import java.io.BufferedReader;
import java.io.FileReader;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import logtree.LogElemLabel;
import logtree.LogElement;

public class PVFS2LogParser implements LogTreeParser {
	
	public PVFS2LogParser() {
		
	}
	
	/**
	 * Get the class label of this message
	 * @param msg This message should include the timestamp
	 * @return
	 */
	public static String getMessageType(String msg) {
		ParseHelper helper = new ParseHelper(msg);		
		String token = helper.nextToken();
		if (token.startsWith("Error")) {
			return token;
		}
		else if (token.startsWith("[") | token.startsWith("(")) {
			return "[]";
		}
		else if (token.startsWith("---")) {
			return "---";
		}
		else if (token.startsWith("bytes") || token.startsWith("metadata") ||
				token.startsWith("request") || token.startsWith("Start") ||
				token.startsWith("Intervals")) {
			return "P";
		}
		else {
			return "op";
		}
	}
	
	public String[] parseLabels(BufferedReader reader) throws Exception {
		// TODO Auto-generated method stub
		return parseLabels(reader, 0, -1);
	}
	
	public List<String> parseForPlain(BufferedReader reader, boolean bExcludeTimestamp) throws Exception {
		return parseForPlain(reader, bExcludeTimestamp, 0, -1);
	}

	
	public List<LogElement> parse(BufferedReader reader) throws Exception {
		return parse(reader, 0, -1);
	}
	
	public String[] parseLabels(BufferedReader reader, int start, int size) throws Exception {
		// TODO Auto-generated method stub
		List<String> messageList = parseForPlain(reader, true, start, size);
		String labels[] = new String[messageList.size()];
		for (int i=0; i<messageList.size(); i++) {
			labels[i] = getMessageType(messageList.get(i));
		}
		return labels;
	}


	public List<String> parseForPlain(BufferedReader reader, boolean bExcludeTimestamp,
			int start, int size) throws Exception {
		// TODO Auto-generated method stub
		int curIndex = 0;
		// Read the first line
		String line = reader.readLine();
		if (line == null)
			return new ArrayList<String>();

		StringBuffer msgBuf = new StringBuffer();
		List<String> messageList = new ArrayList<String>();
		msgBuf.append(line+"\n");
		// Read the second line
		line = reader.readLine();
		while(line != null) {
			if (!ParseHelper.isBlankLine(line)) {
				if (line.charAt(0) == '[') {
					if (curIndex < start) {
						curIndex++;
					}
					else if (size >= 0 && curIndex >= start+size) {
						break;
					}
					else {
						// Parse the previous record
						String message = null;
						if (msgBuf.lastIndexOf("\n") == msgBuf.length()-1) { // If the last char is '\n'
							message = msgBuf.substring(0, msgBuf.length()-1);
						}
						else {
							message = msgBuf.toString();
						}
						if (bExcludeTimestamp) {
							int index = message.indexOf(']');
							String plainText = message.substring(index+1);
							messageList.add(plainText);
						}
						else {
							messageList.add(message);
						}
						curIndex++;
					}
					// For a new record
					msgBuf = new StringBuffer();
					msgBuf.append(line + "\n");
				} else {
					msgBuf.append(line + "\n");
				}
			}
			line = reader.readLine();
		}
		// Add the last record
		if (size < 0 || curIndex < start+size) {
			if (msgBuf.length() > 0) {
				// Parse the previous record
				String message = msgBuf.toString();
				if (msgBuf.lastIndexOf("\n") == msgBuf.length()-1) { // If the last char is '\n'
					message = msgBuf.substring(0, msgBuf.length()-1);
				}
				else {
					message = msgBuf.toString();
				}
				if (bExcludeTimestamp) {
					int index = message.indexOf(']');
					String plainText = message.substring(index+1);
					messageList.add(plainText);
				}
				else {
					messageList.add(message);
				}
			}
		}
		return messageList;
	}
	
	public List<LogElement> parse(BufferedReader reader, int start, int size) throws Exception {
		// TODO Auto-generated method stub
		int curIndex = 0;
		String line = reader.readLine();
		if (line == null)
			return new ArrayList<LogElement>();
		StringBuffer msgBuf = new StringBuffer();
		List<LogElement> elemList = new ArrayList<LogElement>();
		msgBuf.append(line+"\n");
		// Read the second line
		line = reader.readLine();
		while(line != null) {
			if (!ParseHelper.isBlankLine(line)) {				
				if (line.charAt(0) == '[') {
					if (curIndex < start) {
						curIndex++;
					}
					else if (size >= 0 && curIndex >= start+size) {
						break;
					}
					else {
						// Parse the last record
						String message = null;
						if (msgBuf.lastIndexOf("\n") == msgBuf.length()-1) { // If the last char is '\n'
							message = msgBuf.substring(0, msgBuf.length()-1);
						}
						else {
							message = msgBuf.toString();
						}
						LogElement newLogMsg = parseMessage(message);
						elemList.add(newLogMsg);
						curIndex++;
					}
					// For a new record
					msgBuf = new StringBuffer();
					msgBuf.append(line + "\n");
				} else {
					msgBuf.append(line + "\n");
				}
				
			}
			line = reader.readLine();
		}
		// Add the last record
		if (size < 0 || curIndex < start+size) { 
			if (msgBuf.length() > 0) {
				String record = msgBuf.toString();
				elemList.add(parseMessage(record));
			}
		}
		return elemList;
	}

	
	public LogElement parseMessage(String message) throws ParseException {
		ParseHelper helper = new ParseHelper(message);
		LogElement rootE = new LogElement("", LogElemLabel.RECORD);
		LogElement parentE = rootE;
		int pos;
		
		helper.nextChar(); // skip '['
		char sign = helper.nextChar(); // get the sign 
		String date = helper.nextToken();
		String time = helper.nextToken(']');
		Calendar timestamp = parseTimestamp(date, time);
		rootE.setTimestamp(timestamp);
		helper.nextChar(); // skip ']'
		
		int colonIndex = helper.indexOfAtCurLine(": ");
		int commaIndex = helper.indexOfAtCurLine(",");
		if (colonIndex >= 0 && (commaIndex == -1 || commaIndex > colonIndex)) { // "," is behind ":"
			String token = helper.nextToken(": ");
			// If it is a [ ]:
			if (token.startsWith("[") && token.endsWith("]")) {
				parentE.setContent("[]");
				parentE.setLabel(LogElemLabel.STR);
				LogElement nextE = new LogElement(token.substring(1, token.length()-2), LogElemLabel.STR);
				parentE.addChild(nextE);
				parentE = nextE;
			}
			else {
				// skip the ':'
				helper.nextChar();
				token = token.trim();
				parentE.setContent(token);
				parentE.setLabel(LogElemLabel.STR);
			}
		}
		else if (commaIndex >= 0 && (colonIndex == -1 || colonIndex > commaIndex)) { // ":" is behind ","
			String token = helper.nextToken(",");
			// skip the ','
			helper.nextChar();
			token = token.trim();
			parentE.setContent(token);
			parentE.setLabel(LogElemLabel.STR);
		}
		else {
			String token = helper.nextToEnd();
			token = token.trim();
			parentE.setContent(token);
			parentE.setLabel(LogElemLabel.STR);
			return rootE;
		}
		
		if (sign == 'P') { // Printing information from PVFS2-server
			while(helper.hasNextChar()) {
				String token = helper.nextToken();
				LogElement elem = new LogElement(token, LogElemLabel.STR);
				parentE.addChild(elem);
			}
		}
		else { // Other log message
			// Split the rest content of message by ','
			String restContent = helper.nextToEnd();
			char[] splitors = {',', '\n'};
			String[] subContents = ParseHelper.splitWithBreakingBrace(restContent, splitors, '(', ')');
			for (int i=0; i<subContents.length; i++) {
				// Add the events
				helper = new ParseHelper(subContents[i]);
				while(helper.hasNextChar()) {
					pos = helper.getPos();
					String token = helper.nextToken();
					token = token.trim();
					if (token.startsWith("(")) {
						helper.setPos(pos);
						token = helper.nextToken(')');
						token += ')';
						token = token.trim();
						if (helper.hasNextChar()) {
							helper.nextChar(); // skip the ')'
						}
						LogElement eventElem = new LogElement(token, LogElemLabel.ID);
						parentE.addChild(eventElem);
					}
					else if (token.endsWith(":")) {
						LogElement eventElem = new LogElement(token, LogElemLabel.ID);
						String eventContent = "";
						while(helper.hasNextChar()) {
							pos = helper.getPos();
							token = helper.nextToken();
							if (token.startsWith("(") || token.endsWith(":")) {
								helper.setPos(pos); // Recover this token
								break;
							}
							else {
								eventContent += token+" ";
							}
						}
						eventContent = eventContent.trim();
						LogElement fieldElem = new LogElement(eventContent, LogElemLabel.STR);
						eventElem.addChild(fieldElem);
						parentE.addChild(eventElem);
					}
					else {
						helper.setPos(pos); // Restore the parsing the token before
						String eventContent = helper.nextToken('(');
						if (eventContent == null) {
							eventContent = helper.nextToEnd();
						}
						eventContent = eventContent.trim();
						parentE.addChild(new LogElement(eventContent, LogElemLabel.STR));
					}
				
				}
			}
		}
		rootE.updateDepth(0);
		return rootE;
	}
		
	private static Calendar parseTimestamp(String dateText, String timeText) throws ParseException {
		DateFormat fm = new java.text.SimpleDateFormat("MM/dd HH:mm");
		String s = dateText+" "+timeText;
		Date date = fm.parse(s);
		Calendar cal = Calendar.getInstance();
		cal.setTime(date);
		return cal;
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
	}
	
	

}
