package loginsight.logtree.parser;

import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

public class ParseHelper {
	
	private String _str = null;
	private int _index = 0;
	private String _delimters =" \t\r\n";
	
	public ParseHelper(String str) {
		_str = str;
		_index = 0;
	}
	
	public ParseHelper(String str, String delimters) {
		this(str);
		_delimters = delimters;
	}
	
	public String nextNumber() {
		skipBlanks();
		if (_index >= _str.length())
			return "";
		StringBuffer sb = new StringBuffer();
		char ch = _str.charAt(_index);
		while(isDigit(ch)) {
			sb.append(ch);
			_index++;
			if (_index >= _str.length())
				break;
			ch = _str.charAt(_index);
		}
		return sb.toString();
	}
	
	public String nextToken() {
		skipBlanks();
		if (_index >= _str.length())
			return "";
		StringBuffer sb = new StringBuffer();
		char ch = _str.charAt(_index);
		while(!isDelimter(ch)) {
			sb.append(ch);
			_index++;
			if (_index >= _str.length())
				break;
			ch = _str.charAt(_index);
		}
		return sb.toString();
	}
	
	public String peekToken() {
		int oldIndex = _index;
		String token = nextToken();
		_index = oldIndex;
		return token;
	}
	
	/**
	 * Get the next token without the stop char
	 * @param stopChar
	 * @return
	 */
	public String nextToken(char stopChar) {
		skipBlanks();
		if (_index >= _str.length())
			return "";
		StringBuffer sb = new StringBuffer();
		char ch = _str.charAt(_index);
		while(stopChar != ch) {
			sb.append(ch);
			_index++;
			if (_index >= _str.length())
				break;
			ch = _str.charAt(_index);
		}
		return sb.toString();
	}
	
	/**
	 * Get the next token without the stop char
	 * @param stopChar
	 * @param includeStopChar
	 * @return
	 */
	public String nextToken(char stopChar, boolean includeStopChar) {
		skipBlanks();
		if (_index >= _str.length())
			return "";
		StringBuffer sb = new StringBuffer();
		char ch = _str.charAt(_index);
		while(stopChar != ch) {
			sb.append(ch);
			_index++;
			if (_index >= _str.length())
				break;
			ch = _str.charAt(_index);
		}
		if (includeStopChar) {
			sb.append(ch);
			_index++;
		}
		return sb.toString();
	}
	
	/**
	 * Get the next token without the stop char
	 * @param stopChar
	 * @return
	 */
	public String nextToken(char[] stopChars) {
		String stopStr = new String(stopChars);
		skipBlanks();
		if (_index >= _str.length())
			return "";
		StringBuffer sb = new StringBuffer();
		char ch = _str.charAt(_index);
		while(stopStr.indexOf(ch) == -1) {
			sb.append(ch);
			_index++;
			if (_index >= _str.length())
				break;
			ch = _str.charAt(_index);
		}
		return sb.toString();
	}
	
	public String peekToken(char stopChar) {
		int oldIndex = _index;
		String token = nextToken(stopChar);
		_index = oldIndex;
		return token;
	}
	
	public String nextToken(String stopStr) {
		skipBlanks();
		if (_index >= _str.length())
			return "";
		int stopIndex = _str.indexOf(stopStr, _index);
		if (stopIndex == -1)
			return null;
		else {
			String token = _str.substring(_index, stopIndex);
			_index = stopIndex;
			return token;
		}
	}
	
	public String nextToken(String[] stopStrs) {
		skipBlanks();
		if (_index >= _str.length())
			return "";
		int minStopIndex = Integer.MAX_VALUE;
		for (int i=0; i<stopStrs.length; i++) {
			String stopStr = stopStrs[i];
			int stopIndex = _str.indexOf(stopStr, _index);
			if (stopIndex == -1) {
				stopIndex = _str.length();
			}
			minStopIndex = minStopIndex < stopIndex ? minStopIndex: stopIndex;
		}
		String token = _str.substring(_index, minStopIndex);
		_index = minStopIndex;
		return token;
	}
	
	public String nextToEnd() {
		String token = _str.substring(_index);
		_index = _str.length();
		return token;
	}
	
	public char nextChar() {
		return _str.charAt(_index++);
	}
	
	public char nextCharSkipBlank() {
		char ch = _str.charAt(_index++);
		while(isBlank(ch)) {
			if (_index >= _str.length()) 
				return (char)(-1);
			ch = _str.charAt(_index++);
		}
		return ch;
	}
	
	public char peekChar() {
		return _str.charAt(_index);
	}
	
	public char peekCharSkipBlank() {
		int pos = _index;
		char ch = nextCharSkipBlank();
		_index = pos;
		return ch;
	}
	
	public boolean hasNextChar() {
		return _index < _str.length();
	}
	
	public void setPos(int pos) {
		_index = pos;
	}
	
	public int getPos() {
		return _index;
	}
	
	public int indexOfAtCurLine(char ch) {
		String curLine = getCurLine();
		int index = curLine.indexOf(ch);
		if (index >= 0)
			return _index+index;
		else
			return -1;
	}
	
	public int indexOfAtCurLine(String str) {
		String curLine = getCurLine();
		int index = curLine.indexOf(str);
		if (index >= 0)
			return _index+index;
		else
			return -1;
	}
	
	public String getCurLine() {
		StringBuffer sb = new StringBuffer();
		int i=_index;
		if (_index >= _str.length())
			return sb.toString();
		char ch = _str.charAt(i);
		while (ch != '\n') {
			sb.append(ch);
			i++;
			if (i >= _str.length()) 
				break;
			ch = _str.charAt(i);
		}
		return sb.toString();
	}
	
	public void skipBlanks() {
		if (_index >= _str.length())
			return;
		char ch = _str.charAt(_index);
		while(isBlank(ch)) {
			_index++;
			if (_index >= _str.length())
				return;
			ch = _str.charAt(_index);
		}
	}
	
	public static boolean isDigit(char ch) {
		if (ch >= '0' && ch <='9')
			return true;
		else
			return false;
	}
	
	public static boolean isBlank(char ch) {
		if (ch == ' ' || ch == '\t' || ch == '\r' || ch == '\n')
			return true;
		else
			return false;
	}
	
	public boolean isDelimter(char ch) {
		if (_delimters.indexOf(ch) >= 0)
			return true;
		else
			return false;
	}
	
	public static String[] splitWithBreakingBrace(String str,
			char separator,
			char braceStart, 
			char braceEnd) {
		return splitWithBreakingBrace(str, new char[]{separator}, braceStart, braceEnd);
	}
	
	public static String[] splitWithBreakingBrace(String str,
			char[] separators,
			char braceStart, 
			char braceEnd) {
		List<String> strs = new ArrayList<String>();
		StringBuffer sb = new StringBuffer();
		int index=0;
		String sepStr = new String(separators);
		while(index < str.length()) {
			char ch = str.charAt(index);
			if (sepStr.indexOf(ch) >= 0) {
				strs.add(sb.toString());
				sb = new StringBuffer();
			}
			else {
				if (ch == braceStart) {
					sb.append(ch);
					index++;
					while(index < str.length()) {
						ch = str.charAt(index);
						sb.append(ch);
						if (ch == braceEnd) {
							break;
						}
						index++;
					}
				}
				else {
					sb.append(ch);
				}
			}
			index++;
		}
		String endStr = sb.toString();
		if (endStr.length() > 0) {
			strs.add(endStr);
		}
		return strs.toArray(new String[]{});
	}
	
	public static boolean isNumber(String str) {
		for (int i=0; i<str.length(); i++) {
			if (isDigit(str.charAt(i)) == false) {
				return false;
			}
		}
		return true;
	}
	
	public static boolean isBlankLine(String line) {
		for (int i=0; i<line.length(); i++) {
			if (!isBlank(line.charAt(i)))
				return false;
		}
		return true;
	}
	
	public static boolean isTimeFormat(String str) {
		return str.matches("([0-9]*[:/-])+([0-9])*");
	}
	
	public boolean containTimestamp(String line) {
		StringTokenizer tk = new StringTokenizer(line, _delimters);
		while(tk.hasMoreTokens()) {
			String token = tk.nextToken();
			if (ParseHelper.isTimeFormat(token))
				return true;
		}
		return false;
	}
	
	
}
