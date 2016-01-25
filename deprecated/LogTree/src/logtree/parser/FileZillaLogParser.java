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

public class FileZillaLogParser implements LogTreeParser {
	
	
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
		{
			return new ArrayList<String>();
		}
		
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
						String date = helper.nextToken();
						String time = helper.nextToken();
						// Skip two numbers
						helper.nextNumber();
						helper.nextNumber();
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
	
	public LogElement parseMessage(String record) throws ParseException {
		ParseHelper helper = new ParseHelper(record);
		LogElement recordElem = new LogElement("", LogElemLabel.RECORD);
		String date = helper.nextToken();
		String time = helper.nextToken();
		if (!ParseHelper.isTimeFormat(date) || !ParseHelper.isTimeFormat(time)) {
			throw new Error("The date or timestamp is wrong : "+date+" "+time);
		}
		Calendar timestamp = parseTimestamp(date, time);
		recordElem.setTimestamp(timestamp);		
		// Skip two numbers
		helper.nextNumber();
		helper.nextNumber();
		// Retrieve the command or status
		recordElem.setContent(helper.nextToken());
		recordElem.setLabel(LogElemLabel.STR);
		// Retrieve the log message 
		String[] stopStrs = new String[]{": "," \"","\" ",". "};
		String segment = helper.nextToken(stopStrs);
		if (helper.hasNextChar()) {
			helper.nextChar();
		}
		while(segment.length() > 0) {
			recordElem.addChild(new LogElement(segment, LogElemLabel.STR));
			segment = helper.nextToken(stopStrs);
			if (helper.hasNextChar()) {
				helper.nextChar();
			}
		}
		recordElem.updateDepth(0);
		return recordElem;
	}
	
	private static Calendar parseTimestamp(String dateText, String timeText) throws ParseException {
		DateFormat fm = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
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
		// DJC test2();
	}
	
	private static void test2() {
		try {
			String filename = "filezilla.log";
			FileZillaLogParser parser = new FileZillaLogParser();
			List<LogElement> logElems = parser.parse(new BufferedReader(new FileReader(filename)), 0, -1);
			FileOutputStream out = new FileOutputStream("out_filezilla.txt");
			PrintStream outPrint = new PrintStream(out);
			LogElement rootElem = new LogElement(logElems);
			rootElem.updateDepth(0);
			rootElem.print(outPrint);
			out.close();
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	private static void test1() {
		try{
			String str="[D 04/27 04:59] [SM Locating]: (0x952e1a0) located: unexpected_sm:post_unexpected";
			MySQLLogParser parser = new MySQLLogParser();
			LogElement logElem = parser.parseRecord(str);
			logElem.print(System.out);
			
			str = "4/14/2010	11:35:34 AM	McLogEvent	Information	None	257	NT AUTHORITY\\SYSTEM	PERSISTENT	Would be blocked by access protection rule  (rule is in warn-only mode) (Common Standard Protection:Prevent common programs from running files from the Temp folder).";
			logElem = parser.parseRecord(str);
			logElem.print(System.out);
			
			str = "100403 17:39:09  InnoDB: Started; log sequence number 0 44233";
			logElem = parser.parseRecord(str);
			logElem.print(System.out);
		}catch(Exception e) {
			e.printStackTrace();
		}
	}

}
