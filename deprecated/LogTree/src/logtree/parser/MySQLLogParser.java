package logtree.parser;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.PrintStream;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

import logtree.LogElemLabel;
import logtree.LogElement;

public class MySQLLogParser implements LogTreeParser{
	
	public static String delimters =" \t\r\n";
	
	public MySQLLogParser() {
		
	}
	
	public static String getMessageType(String msg) {
		ParseHelper helper = new ParseHelper(msg);
		return helper.nextToken();
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

		StringBuffer recordSB = new StringBuffer();
		List<String> messageList = new ArrayList<String>();
		recordSB.append(line+"\n");
		// Read the second line
		line = reader.readLine();
		while(line != null) {
			ParseHelper helper = new ParseHelper(line);
			if (!ParseHelper.isBlankLine(line)) {
				String firstToken = helper.nextToken();
				if (ParseHelper.isNumber(firstToken)) {
					if (curIndex < start) {
						curIndex++;
					}
					else if (size >= 0 && curIndex >= start+size) {
						break;
					}
					else {
						// Parse the last record
						String record = recordSB.toString();
						if (bExcludeTimestamp) {
							ParseHelper lineHelper = new ParseHelper(record);
							String dateText = lineHelper.nextNumber();
							String timeText = lineHelper.nextToken();
							messageList.add(lineHelper.nextToEnd());
						}
						else {
							messageList.add(record);
						}
						curIndex++;
					}
					// For a new record
					recordSB = new StringBuffer();
					recordSB.append(line + "\n");
					
				} else {
					recordSB.append(line + "\n");
				}
			}
			line = reader.readLine();
		}
		// Add the last record
		if (size < 0 || curIndex < start+size) { 
			if (recordSB.length() > 0) {
				String record = recordSB.toString();
				if (bExcludeTimestamp) {
					ParseHelper lineHelper = new ParseHelper(record);
					String dateText = lineHelper.nextNumber();
					String timeText = lineHelper.nextToken();
					messageList.add(lineHelper.nextToEnd());
				}
				else {
					messageList.add(record);
				}
			}
		}
		return messageList;
	}

	public List<LogElement> parse(BufferedReader reader, int start, int size) throws Exception {
		int curIndex = 0;
		// Read the first line
		String line = reader.readLine();
		if (line == null)
			return new ArrayList<LogElement>();

		StringBuffer recordSB = new StringBuffer();
		List<LogElement> elemList = new ArrayList<LogElement>();
		recordSB.append(line+"\n");
		// Read the second line
		line = reader.readLine();
		while(line != null) {
			ParseHelper helper = new ParseHelper(line);
			if (!ParseHelper.isBlankLine(line)) {
				String firstToken = helper.nextToken();
				if (ParseHelper.isNumber(firstToken)) {
					if (curIndex < start) {
						curIndex++;
					}
					else if (size >= 0 && curIndex >= start+size) {
						break;
					}
					else {
						// Parse the last record
						String record = recordSB.toString();
						LogElement newLogMsg = parseRecord(record);
						elemList.add(newLogMsg);
						// For a new record
						recordSB = new StringBuffer();
						recordSB.append(line + "\n");
						
						curIndex++;
					}
				} else {
					recordSB.append(line + "\n");
				}
			}
			line = reader.readLine();
		}
		// Add the last record
		if (size < 0 || curIndex < start+size) {
			if (recordSB.length() > 0) {
				String record = recordSB.toString();
				elemList.add(parseRecord(record));
			}
		}
		return elemList;
	}
	
	public LogElement parseRecord(String message) throws ParseException {
		ParseHelper helper = new ParseHelper(message);
		LogElement rootE = new LogElement("", LogElemLabel.RECORD);
		// Add the log record ID
		String dateText = helper.nextNumber();
		String timeText = helper.nextToken();
		Calendar cal = parseTimestamp(dateText, timeText);
		rootE.setTimestamp(cal);
		// If it is a []
		String token = helper.peekToken();
		if (token.startsWith("[")) {
			rootE.setContent(token);
			rootE.setLabel(LogElemLabel.STR);
			helper.nextToken();
		}
		// Add the events
		while(helper.hasNextChar()) {
			int colonPos = helper.indexOfAtCurLine(": ");
			if (colonPos > 0) {
				String eventName = helper.nextToken(": ");
				LogElement eventElem = new LogElement(eventName, LogElemLabel.ID);
				helper.setPos(colonPos+1);
				String eventContent = helper.nextToken(new String[]{"\n","  "});
				eventElem.addChild(new LogElement(eventContent, LogElemLabel.STR));
				rootE.addChild(eventElem);
			}
			else {
				String eventContent = helper.nextToken("\n");
				rootE.addChild(new LogElement(eventContent, LogElemLabel.STR));
			}
			
			if (helper.hasNextChar()) {
				helper.nextChar();
			}
			else { // No more char
				break;
			}
		}
		rootE.updateDepth(0);
		return rootE;
	}
	
	private static Calendar parseTimestamp(String dateText, String timeText) throws ParseException {
		DateFormat fm = new java.text.SimpleDateFormat("yyMMdd HH:mm:ss");
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
