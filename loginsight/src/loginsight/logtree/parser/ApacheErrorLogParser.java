package loginsight.logtree.parser;

import java.io.BufferedReader;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import loginsight.logtree.LogElemLabel;
import loginsight.logtree.LogElement;

public class ApacheErrorLogParser implements LogTreeParser {
	
	/**
	 * 
	 * @param msg This message should not include the time-stamp
	 * @return
	 */
	public static String getMessageType(String msg) {
		ParseHelper helper = new ParseHelper(msg);
		// skip the '[error]'
		helper.nextToken(']', true);
		
		// skip the '[client ...]'
		char ch = helper.peekCharSkipBlank();
		if (ch == '[') {
			helper.nextToken(']', true);
		}
		else if (ch == '(') {
			helper.nextToken(')', true);
		}
		String errorDesc;
		int colonIndex = helper.indexOfAtCurLine(": ");
		if (colonIndex < 0) {
			errorDesc = helper.nextToEnd();
		}
		else {
			errorDesc = helper.nextToken(": ");
		}
		String label = null;
		if (errorDesc.indexOf("not exist") != -1 || errorDesc.indexOf("not found") != -1) {
			label = "404";
		}
		else if (errorDesc.indexOf("No such file or directory")!= -1) {
			label = "500";
		}
		else if (errorDesc.indexOf("Invalid method") != -1 ||
				errorDesc.indexOf("client sent HTTP") !=-1) {
			label = "400";
		}
		else if (errorDesc.indexOf("Permission") != -1) {
			label = "403"; 
		}
		else {
			label = "others";
		}
		// System.out.println(label+"\t"+errorDesc);
		return label;
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
	
	public List<String> parseForPlain(BufferedReader reader,
			boolean bExcludeTimestamp, int start, int size) throws Exception {
		// TODO Auto-generated method stub
		int curIndex = 0;
		// Read the first line
		String line = reader.readLine();
		if (line == null)
			return new ArrayList<String>();
		List<String> messageList = new ArrayList<String>();
		// Read the second line
		while(line != null) {
			if (!ParseHelper.isBlankLine(line)) {
				if (curIndex < start) {
					curIndex++;
				} else if (size >= 0 && curIndex >= start + size) {
					break;
				} else {
					if (bExcludeTimestamp) {
						ParseHelper helper = new ParseHelper(line);
						// Skip to '[error]'
						helper.nextToken(']', true);
						messageList.add(helper.nextToEnd());
					} else {
						messageList.add(line);
					}
					curIndex++;
				}
			}
			line = reader.readLine();
		}
		return messageList;
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

	public List<LogElement> parse(BufferedReader reader, int start, int size) throws Exception {
		// TODO Auto-generated method stub
		int curIndex = 0;
		// Read the first line
		String line = reader.readLine();
		if (line == null)
			return new ArrayList<LogElement>();
		List<LogElement> elemList = new ArrayList<LogElement>();
		// Read the second line
		while(line != null) {
			if (!ParseHelper.isBlankLine(line)) {
				if (curIndex < start) {
					curIndex++;
				}
				else if (size >= 0 && curIndex >= start+size) {
					break;
				}
				else {
					LogElement e = parseMessage(line);
					elemList.add(e);
					curIndex++;
				}
			}
			line = reader.readLine();
		}
		return elemList;
	}
	
	public LogElement parseMessage(String message) throws ParseException {
		ParseHelper helper = new ParseHelper(message);
		LogElement rootElem = new LogElement("", LogElemLabel.RECORD);
		
		// skip the '['
		helper.nextChar();
		String dayInWeek = helper.nextToken();
		String month = helper.nextToken();
		String day = helper.nextToken();
		String time = helper.nextToken();
		String year = helper.nextNumber();
		// skip the ']'
		helper.nextChar();		
		Calendar timestamp = parseTimestamp(dayInWeek, month,day, year, time);
		rootElem.setTimestamp(timestamp);	
		
		// Skip '[error]'
		helper.nextToken();
		
		// Skip '[client <IP>]'
		char ch = helper.peekCharSkipBlank();
		if (ch == '[') {
			String clientToken = helper.nextToken(']', true);
			LogElement clientElem = new LogElement(clientToken, LogElemLabel.STR);
			rootElem.addChild(clientElem);
		}
		else if (ch == '(') {
			// Skip the '(<num>)'
			helper.nextToken(')', true);
		}
				
		// Retrieve the command or status
		int colonIndex = helper.indexOfAtCurLine(": ");
		int commaIndex = -1;
		if (colonIndex > 0) {
			ch = helper.peekCharSkipBlank();
			if (ch == '(') {
				// Skip the '(<num>)'
				helper.nextToken(')', true);
			}
			String errDesc = helper.nextToken(": ");
			rootElem.setContent(errDesc);
			rootElem.setLabel(LogElemLabel.STR);
			// skip ": "
			helper.nextChar();
			helper.nextChar();
			commaIndex = helper.indexOfAtCurLine(", ");
			if (commaIndex > 0) {
				String errTarget = helper.nextToken(", ");
				LogElement targetElem = new LogElement(errTarget, LogElemLabel.STR);
				rootElem.addChild(targetElem);
			}
			else {
				String errTarget = helper.nextToEnd();
				LogElement targetElem = new LogElement(errTarget, LogElemLabel.STR);
				rootElem.addChild(targetElem);
			}
		}
		else {
			rootElem.setContent(helper.nextToEnd());
		}
		
		while(commaIndex > 0) {
			// Skip the ','
			helper.nextChar();
			colonIndex = helper.indexOfAtCurLine(": ");
			commaIndex = -1;
			if (colonIndex > 0) {
				String errDesc = helper.nextToken(": ");
				LogElement anotherElem = new LogElement(errDesc, LogElemLabel.STR);
				commaIndex = helper.indexOfAtCurLine(", ");
				if (commaIndex > 0) {
					String errTarget = helper.nextToken(", ");
					LogElement targetElem = new LogElement(errTarget, LogElemLabel.STR);
					anotherElem.addChild(targetElem);
				}
				else {
					String errTarget = helper.nextToEnd();
					LogElement targetElem = new LogElement(errTarget, LogElemLabel.STR);
					anotherElem.addChild(targetElem);
				}
				rootElem.addChild(anotherElem);
			}
			else {
				String token = helper.nextToEnd();
				if (token != null && token.length() > 0) {
					LogElement anotherElem = new LogElement(token, LogElemLabel.STR);
					rootElem.addChild(anotherElem);
				}
			}
		}
		
		rootElem.updateDepth(0);
		// rootElem.print(System.out);
		return rootElem;
	}
	
	private static Calendar parseTimestamp(String dayInWeek,
			String month, String day, 
			String year, String timeText) throws ParseException {
		DateFormat fm = new java.text.SimpleDateFormat("EEE MMM dd HH:mm:ss yyyy");
		String s = dayInWeek+" "+month+" "+day+" "+timeText+ " "+year;
		Date date = fm.parse(s);
		Calendar cal = Calendar.getInstance();
		cal.setTime(date);
		return cal;
	}


}
