package core;
import java.util.StringTokenizer;

public class LabeledStringMactchSimilairty implements SimilarityFunction {
	
	enum WordLabel {
		STR,
		NUMBER,
		MARK,
		COMMENT,
	}
	
	String _marks = "[]()";
	String _delim = _marks+" \t\r\n";
	String numRegex = "(0x\\d+)|[\\d.:]+";
	double w = 0.1;
	
	public void setTypeMatchWeight(double w) {
		this.w = w;
	}
	
	protected WordLabel getWordLabel(String s) {
		char ch = s.charAt(0);
		if (_marks.indexOf(ch) >= 0) {
			return WordLabel.MARK;
		}
		else if(Character.isDigit(ch)) {
			if (s.matches(numRegex))
				return WordLabel.NUMBER;
			else
				return WordLabel.STR;
		}
		else if(s.startsWith("---")) {
			return WordLabel.COMMENT;
		}
		else
			return WordLabel.STR;
	}
	
	public double similarity(Object o1, Object o2) {
		// TODO Auto-generated method stub
		String s1 = (String)o1;
		String s2 = (String)o2;
		if (s1.length() == 0 || s2.length() == 0)
			return 0.0;
		
		StringTokenizer st1 = new StringTokenizer(s1, _delim, true);
		StringTokenizer st2 = new StringTokenizer(s2, _delim, true);
		int len1 = 0;
		int len2 = 0;
		boolean bEOF1 = false;
		boolean bEOF2 = false;
		String t1 = null;
		String t2 = null;
		double score = 0.0;
		while(true) {
			if (st1.hasMoreTokens()) {
				t1 = st1.nextToken();
				// Skip whitespace of t1
				while(Character.isWhitespace(t1.charAt(0))) {
					if (!st1.hasMoreTokens()) {
						bEOF1 = true;
						break;
					}
					t1 = st1.nextToken();
				}
			}
			else {
				bEOF1 = true;
			}

			
			if (st2.hasMoreTokens()) {
				t2 = st2.nextToken();
				// Skip whitespace of t2
				while (Character.isWhitespace(t2.charAt(0))) {
					if (!st2.hasMoreTokens()) {
						bEOF2 = true;
						break;
					}
					t2 = st2.nextToken();
				}
			} else {
				bEOF2 = true;
			}

			if (!bEOF1 && !bEOF2) {
				len1++;
				len2++;
				WordLabel l1 = getWordLabel(t1);
				WordLabel l2 = getWordLabel(t2);
				if (l1 == l2) {
					score += w;
					if (t1.equals(t2)) {
						score += 1-w;
					}
				}				
			}
			else if (bEOF1 && !bEOF2) {
				len2++;
				while(st2.hasMoreTokens()) {					
					t2 = st2.nextToken();
					if (!Character.isWhitespace(t2.charAt(0))){
						len2++;
					}
				}
				break;
			}
			else if (!bEOF1 && bEOF2) {
				len1++;
				while(st1.hasMoreTokens()) {					
					t1 = st1.nextToken();
					if (!Character.isWhitespace(t1.charAt(0))){
						len1++;
					}
				}
				break;
			}
			else {
				break;
			}			
		}
		// System.out.println(""+o1+", "+o2+" : "+score+" lens:("+len1+","+len2+") : "+score / Math.sqrt(len1*len2));
		return score / Math.sqrt(len1*len2);	
	}

}
