package logtree;

import java.awt.BorderLayout;
import java.awt.Container;
import java.awt.Cursor;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;

import clustering.ClusteredLogEvent;
import clustering.ClusteredLogEventType;
import clustering.SingleLinkage;
import clustering.TreeSegDictBuilder;
import core.SymmetricMatrix;
import core.TreeNode;
import core.TreeSimilarity;
import helper.Base64Coder;
import logtree.FastMsgTreeSimilarity;
import logtree.LogElement;
import logtree.parser.ApacheErrorLogParser;
import logtree.parser.FileZillaLogParser;
import logtree.parser.LogTreeParser;
import logtree.parser.MySQLLogParser;
import logtree.parser.PVFS2LogParser;

import org.dom4j.Document;
import org.dom4j.DocumentFactory;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;




@SuppressWarnings("serial")
public class LogTree {
		
	SingleLinkage _sl = null;
    String _curFileName = null;
    List<LogElement> _logList = null;
    List<String> _logMsgList = null;
	int _numEvents = -1;
	
	public LogTree() {
	}
	
 	private void startCreatingEvents(int parserChoice, int loadStartPos, int loadLength) {
		try {
			// Create the log parser
			LogTreeParser parser = null;
			
			// Identify parser to use
			switch(parserChoice) {
			case 0:
				parser = new FileZillaLogParser();
				break;
			case 1:
				parser = new MySQLLogParser();
				break;
			case 2:
				parser = new PVFS2LogParser();
				break;
			case 3:
				parser = new ApacheErrorLogParser();
				break;
			default:
				throw new Error("Unknown type of log type!");
			}
			
			assert(_curFileName != null);
												
			System.out.println("Parsing the log file...");
			
			// Build list of trees from log file
			_logList = parser.parse(new BufferedReader(
					new FileReader(_curFileName)), loadStartPos, loadLength);
			
			// Store list of strings from log file
			_logMsgList = parser.parseForPlain(new BufferedReader(
					new FileReader(_curFileName)), true, loadStartPos, loadLength);
			
			System.out.println("Assessing Similarity...");
						
			// Build similarity matrix for clustering 
			TreeSimilarity simFunc =  new FastMsgTreeSimilarity();
			TreeSegDictBuilder simMatrixBuilder = new TreeSegDictBuilder(_logList);
			SymmetricMatrix simMatrix = simMatrixBuilder.build();
			_sl = new SingleLinkage(_logList, simFunc);
			_sl.setSimMatrix(simMatrix);
			_sl.build();					
						
			System.out.println("Designating " + _numEvents + " Clusters...");
			
			// Determining Centroids in order to assign Cluster IDs
			int[] centers = _sl.getClusterCentroids(_numEvents);

			// Prepare output file name and path based on input file name	
			File outputFile = new File(_curFileName);
			String _absPath = outputFile.getAbsolutePath();
			String _curPath = _absPath.substring(0, _absPath.lastIndexOf(File.separator));
			_curFileName = outputFile.getName();
			
			System.out.println("Sending results to file: " + _curPath + "/LogTree_"+ _numEvents + "_" + _curFileName);			
			
			// Output results to file named "LogTree_" & number of clusters & input file name
			List<LogElement> results = new ArrayList<LogElement>();
			_sl.getInsts(results);
			FileOutputStream out = new FileOutputStream(_curPath + "/LogTree_"+ _numEvents + "_" + _curFileName);			
			PrintStream outPrint = new PrintStream(out);

			// Output timestamp, clusterid, original log entry line
			for (int i=0; i<results.size(); i++) {
			    outPrint.print((int)(results.get(i).getTimestamp().getTimeInMillis()/1000));	
				outPrint.print("," + _sl.getClusterId(i, centers) + ",");
                outPrint.print(_logMsgList.get(i));
                outPrint.println();                				
			}			
			out.close();
			
		}catch(Exception e) {
			e.printStackTrace();
		}
	}	
					
	/**
	 * @param args
	 * Arguments: 
	 * ParserType StartLine EndLine InputFileName NumClusters
	 * Note: 
	 * ParserType 0=FileZilla, 1=MySQL, 2=PVFS2, 3=ApacheError
	 * StartLine=0 starts at first line
	 * EndLine=-1 does ALL log lines
	 */
	public static void main(String[] args) {
		try {
			LogTree MagicHour = new LogTree();        		
			MagicHour._curFileName = args[3];
  			MagicHour._numEvents = Integer.parseInt(args[4]);
  			MagicHour.startCreatingEvents(Integer.parseInt(args[0]), Integer.parseInt(args[1]), Integer.parseInt(args[2]));
						
		}catch(Exception e) {
			e.printStackTrace();
		}
	}


}
