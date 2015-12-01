package loginsight.gui.simpleviewer;

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
import java.util.ArrayList;
import java.util.List;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSlider;
import javax.swing.JTextArea;
import javax.swing.SwingConstants;
import javax.swing.UIManager;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import loginsight.clustering.ClusteredLogEvent;
import loginsight.clustering.ClusteredLogEventType;
import loginsight.clustering.SingleLinkage;
import loginsight.clustering.TreeSegDictBuilder;
import loginsight.core.SymmetricMatrix;
import loginsight.core.TreeNode;
import loginsight.core.TreeSimilarity;
import loginsight.gui.visualization.TreeVisualPanel;
import loginsight.helper.Base64Coder;
import loginsight.logtree.FastMsgTreeSimilarity;
import loginsight.logtree.LogElement;
import loginsight.logtree.parser.ApacheErrorLogParser;
import loginsight.logtree.parser.FileZillaLogParser;
import loginsight.logtree.parser.LogTreeParser;
import loginsight.logtree.parser.MySQLLogParser;
import loginsight.logtree.parser.PVFS2LogParser;

import org.dom4j.Document;
import org.dom4j.DocumentFactory;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;

@SuppressWarnings("serial")
public class SimpleLogViewer extends JFrame implements ActionListener, ChangeListener{
	
	JMenuItem _openLogFileMenuItem;
    JMenuItem _openMSLFileMenuItem;
    JMenuItem _saveMSLFileMenuItem;
    JMenuItem _exitProgramMenuItem;
    JLabel _currentFilePathLabel;
    JScrollPane _logTextPane;
    JTextArea _logTextArea;
    JComboBox _parserChooseCombox;
    final static String[] _parserChoices = {
    	"FileZilla",
    	"MySQL",
    	"PVFS2-Server",
    	"Apache HTTP Server"
    };
    JComboBox _loadStartPosCombox;
    final static String[] _loadStartPositions = {
    	"0",
    	"1000",
    	"2000",
    	"3000",
    	"4000"
    };
    JComboBox _loadLengthCombox;
    final static String[] _loadLengthes = {
    	"ALL",
    	"1000",
    	"2000",
    	"3000",
    	"4000",
    	"5000",
    };
    
    
    JButton _startCreatingEventsButton;
    JSlider _numEventsSlider;
    JButton _showEventTimeLineButton;
    JButton _showEventHistButton;

    JCheckBox _enableFullDispVertexCheckBox;
    JCheckBox _enableDispTimestampCheckBox;
    
    JPanel _centerPanel = null;
    TreeVisualPanel _treeVizPanel = null;
    SingleLinkage _sl = null;
    List<LogElement> _visForest = null;
        
    String _curFileName = null;
    List<LogElement> _logList = null;
    List<String> _logMsgList = null;
	int _numEvents = -1;
	
	EventTimeLineDialog _eventTimeLineDlg = null;
	EventHistogramDialog _eventHistDlg = null;
	
	public SimpleLogViewer() {
		//this.setPreferredSize(new Dimension(500,600));
		super("Simple Textual Log Visualization Viewer");
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		// Create the menu bar
		this.setJMenuBar(createMenuBar()); 
				
		Container contentPane = this.getContentPane();
		contentPane.setLayout(new BorderLayout(5,5));
				
		// Create the north panel
		JPanel northPanel = new JPanel();
		northPanel.setLayout(new BorderLayout(2,2));

		JPanel northNorthPanel  =new JPanel();
		_currentFilePathLabel = new JLabel("Current File: ");
		northNorthPanel.setLayout(new FlowLayout(FlowLayout.LEFT));
		northNorthPanel.add(_currentFilePathLabel);
		_parserChooseCombox = new JComboBox(_parserChoices);
		_parserChooseCombox.setEnabled(false);
		northNorthPanel.add(_parserChooseCombox);
		northPanel.add(northNorthPanel, BorderLayout.NORTH);
		
		northNorthPanel.add(new JLabel("Start Pos: "));
		_loadStartPosCombox = new JComboBox(_loadStartPositions);
		_loadStartPosCombox.setEditable(true);
		northNorthPanel.add(_loadStartPosCombox);
		_loadLengthCombox = new JComboBox(_loadLengthes);
		_loadLengthCombox.setEditable(true);
		northNorthPanel.add(new JLabel("Length: "));
		northNorthPanel.add(_loadLengthCombox);
		
		_logTextArea = new JTextArea("", 5, 50);
		_logTextArea.setLineWrap(false);
		_logTextArea.setEditable(false);
		_logTextPane = new JScrollPane(_logTextArea);
		northPanel.add(_logTextPane, BorderLayout.CENTER);
		
		northPanel.setPreferredSize(new Dimension(400, 300));
		contentPane.add(northPanel, BorderLayout.NORTH);
		
		// Create the center panel
		_centerPanel = new JPanel();
		_centerPanel.setLayout(new BorderLayout(2,2));
		// GROSSMAN _treeVizPanel = new TreeVisualPanel(new ArrayList<TreeNode>());
		_treeVizPanel.setEnabled(false);
		_centerPanel.add(_treeVizPanel, BorderLayout.CENTER);
		
		// Create the center north panel
		JPanel centerNorthPanel = new JPanel();
		centerNorthPanel.setLayout(new FlowLayout(FlowLayout.LEFT));
		
		
		// centerNorthPanel.add(new JLabel(" "));
		_startCreatingEventsButton = new JButton("Start Clustering");
		_startCreatingEventsButton.addActionListener(this);
		_startCreatingEventsButton.setEnabled(false);
		centerNorthPanel.add(_startCreatingEventsButton);
		centerNorthPanel.add(new JLabel(" Num of Events: "));
		_numEventsSlider = new JSlider(SwingConstants.HORIZONTAL, 0, 100, 10);
		_numEventsSlider.addChangeListener(this);
		_numEventsSlider.setPaintTicks(true);
		_numEventsSlider.setPaintLabels(true);
		_numEventsSlider.setMajorTickSpacing(5);
		_numEventsSlider.setMinorTickSpacing(5);
		Dimension d = _numEventsSlider.getPreferredSize();
		d.width = d.width*2;
		_numEventsSlider.setPreferredSize(d);
		_numEventsSlider.setEnabled(false);
		centerNorthPanel.add(_numEventsSlider);
		_showEventTimeLineButton = new JButton("Event Timeline");
		_showEventTimeLineButton.addActionListener(this);
		_showEventTimeLineButton.setEnabled(false);
		centerNorthPanel.add(_showEventTimeLineButton);
		_showEventHistButton  = new JButton("Event Histogram");
		_showEventHistButton.addActionListener(this);
		_showEventHistButton.setEnabled(false);
		centerNorthPanel.add(_showEventHistButton);
		_centerPanel.add(centerNorthPanel, BorderLayout.NORTH);
		
		// Create the center east panel
		JPanel centerEastPanel = new JPanel();
		centerEastPanel.setLayout(new BoxLayout(centerEastPanel, BoxLayout.Y_AXIS));
		_enableFullDispVertexCheckBox = new JCheckBox("Full display vertex");
		_enableFullDispVertexCheckBox.setSelected(false);
		_enableFullDispVertexCheckBox.addActionListener(this);
		centerEastPanel.add(_enableFullDispVertexCheckBox);
		_enableDispTimestampCheckBox = new JCheckBox("Display Timestamp");
		_enableDispTimestampCheckBox.setSelected(true);
		_enableDispTimestampCheckBox.addActionListener(this);
		centerEastPanel.add(_enableDispTimestampCheckBox);
		_centerPanel.add(centerEastPanel, BorderLayout.EAST);
				
		contentPane.add(_centerPanel, BorderLayout.CENTER);
	}
	
	public JMenuBar createMenuBar() {
        JMenuBar menuBar;
        JMenu fileMenu;
        JMenu exitMenu;
        JMenu helpMenu;
        
        //Create the menu bar.
        menuBar = new JMenuBar();

        // Build the File menu.
        fileMenu = new JMenu("File");
        fileMenu.getAccessibleContext().setAccessibleDescription(
                "The only menu in this program that has menu items");
        menuBar.add(fileMenu);
        
        _openLogFileMenuItem = new JMenuItem("Open log file");
        _openLogFileMenuItem.getAccessibleContext().setAccessibleDescription(
        		"Open log file");
        _openLogFileMenuItem.addActionListener(this);
        fileMenu.add(_openLogFileMenuItem);
                
        fileMenu.addSeparator();
        
        _openMSLFileMenuItem = new JMenuItem("Open clustering result file");
        _openMSLFileMenuItem.getAccessibleContext().setAccessibleDescription(
                "Open clustering result file");
        _openMSLFileMenuItem.addActionListener(this);
        fileMenu.add(_openMSLFileMenuItem);
        
        _saveMSLFileMenuItem = new JMenuItem("Save clustering result file");
        _saveMSLFileMenuItem.getAccessibleContext().setAccessibleDescription(
                "Save clustering result file");
        _saveMSLFileMenuItem.addActionListener(this);
        fileMenu.add(_saveMSLFileMenuItem);
        
        // Build the Exit menu
        exitMenu = new JMenu("Exit");
        menuBar.add(exitMenu);
        _exitProgramMenuItem = new JMenuItem("Exit Program");
        _exitProgramMenuItem.getAccessibleContext().setAccessibleDescription("Exit Program");
        _exitProgramMenuItem.addActionListener(this);
        exitMenu.add(_exitProgramMenuItem);
        
        // Build the Help menu
        helpMenu = new JMenu("Help");
        menuBar.add(helpMenu);
        
        return menuBar;
    }


	public void actionPerformed(ActionEvent e) {
		// TODO Auto-generated method stub
		if (e.getSource() == _openMSLFileMenuItem) {
			JFileChooser fc = new JFileChooser();
			fc.setCurrentDirectory(new File("."));
			fc.setMultiSelectionEnabled(false);
	        int returnVal = fc.showOpenDialog(this);
	        if (returnVal == JFileChooser.APPROVE_OPTION) {
		        String filename = fc.getSelectedFile().getPath();
		        openClusteringResultFile(filename);
	        }
		}
		else if (e.getSource() == _saveMSLFileMenuItem) {
			JFileChooser fc = new JFileChooser();
			fc.setCurrentDirectory(new File("."));
			fc.setMultiSelectionEnabled(false);
	        int returnVal = fc.showSaveDialog(this);
	        if (returnVal == JFileChooser.APPROVE_OPTION) {
		        String filename = fc.getSelectedFile().getPath();
		        saveClusteringResultFile(filename);
		        JOptionPane.showMessageDialog(this, "Save the file OK!");
	        }
		}
		else if (e.getSource() == _openLogFileMenuItem) {
			// Create the file dialog
			JFileChooser fc = new JFileChooser();
			fc.setCurrentDirectory(new File("."));
			fc.setMultiSelectionEnabled(false);
	        int returnVal = fc.showOpenDialog(this);
	        if (returnVal == JFileChooser.APPROVE_OPTION) {
		        String filename = fc.getSelectedFile().getPath();
		        // Read the log content
		        openLogFile(filename);
		        this.invalidate();
	        }
		}
		else if (e.getSource() == _enableFullDispVertexCheckBox) {
			boolean bFullDisp = _enableFullDispVertexCheckBox.isSelected();
			// GROSSMAN _treeVizPanel.setEnableShortLabel(!bFullDisp);
			this.invalidate();
		}
		else if (e.getSource() == _enableDispTimestampCheckBox) {
			List<LogElement> forest = new ArrayList<LogElement>();
			_sl.getClusterCentroids(_numEvents, forest);
			boolean bDispTime = _enableDispTimestampCheckBox.isSelected();
			_visForest = prepareLogForestForVis(forest, bDispTime);
			// GROSSMAN		_treeVizPanel.updateForest(_visForest);
			this.invalidate();
		}
		else if (e.getSource() == _showEventTimeLineButton) {
			openEventTimeLineDialog();
		}
		else if (e.getSource() == _showEventHistButton) {
			openEventHistogramDialog();
		}
		else if (e.getSource() == _startCreatingEventsButton) {			
			startCreatingEvents();
		}
		else if(e.getSource() == _exitProgramMenuItem) {
			System.exit(EXIT_ON_CLOSE);
		}
	}

	public void stateChanged(ChangeEvent e) {
		// TODO Auto-generated method stub
		if (e.getSource() == _numEventsSlider) {
			int numClusters = _numEventsSlider.getValue();
			_numEvents = numClusters;
			List<LogElement> forest = new ArrayList<LogElement>();
			_sl.getClusterCentroids(_numEvents, forest);
			boolean bDispTime = _enableDispTimestampCheckBox.isSelected();
			_visForest = prepareLogForestForVis(forest, bDispTime);
			// Update the tree panel
			// GROSSMAN	_treeVizPanel.updateForest(_visForest);
			// Update the event timeline dialog
			if (_eventTimeLineDlg != null) {
				updateEventTimeLineDialog();
			}
			// Update the event histogram dialog
			if (_eventHistDlg != null) {
				updateEventHistogramDialog();
			}
			
			int[] centers = _sl.getClusterCentroids(_numEvents);
			for (int i=0; i<forest.size(); i++) {
				System.out.println(i+" : "+_logMsgList.get(centers[i]));
			}
			this.invalidate();
		}
	}
	
	private void openLogFile(String filename) {
		try {
			this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
			BufferedReader reader = new BufferedReader(new FileReader(filename));
			String line = null;
			StringBuffer sb = new StringBuffer();
			while((line = reader.readLine()) != null) {
				sb.append(line);
				sb.append("\n");
			}
			_logTextArea.setText(sb.toString());
			_curFileName = filename;
			_currentFilePathLabel.setText("Current File: "+filename);
			updateComponentsEnableStatus();
			this.setCursor(Cursor.getDefaultCursor());
		}catch(IOException e) {
			e.printStackTrace();
		}
	}
	
	private void openClusteringResultFile(String filename)  {
		try {
			this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
			// Open the DOM reader
			File xmlFile = new File(filename);
			SAXReader reader = new SAXReader();
		    Document doc = reader.read(xmlFile);
		    Element root = doc.getRootElement();
		    
		    // Read the clustering result
		    _sl = new SingleLinkage();			
		    _sl.fromDOM(root.element("SL"));
		    _logList = new ArrayList<LogElement>();
		    _sl.getInsts(_logList);

		    // Read the original log text
		    String encodedLogText = root.elementText("logs");
		    String originalLogText = Base64Coder.decodeString(encodedLogText);
			_logTextArea.setText(originalLogText);
			_logTextArea.setEnabled(true);
			_startCreatingEventsButton.setEnabled(true);
			_numEventsSlider.setEnabled(true);
			
			// Read the current summarize level
			_numEvents = Integer.parseInt(root.elementText("summarizelevel"));
			
			// Set the current file path
			_currentFilePathLabel.setText("Current File: "+filename);
			
			// Refresh the log visualization panel
			List<LogElement> forest = new ArrayList<LogElement>();
			_sl.getClusterCentroids(_numEvents, forest);
			boolean bDispTime = _enableDispTimestampCheckBox.isSelected();
			_visForest = prepareLogForestForVis(forest, bDispTime);
			// GROSSMAN    _treeVizPanel.updateForest(_visForest);
	        updateComponentsEnableStatus();
	        this.invalidate();
	        this.setCursor(Cursor.getDefaultCursor());
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	private void saveClusteringResultFile(String filename) {
		try {
			this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
			// Create the DOM Document
			Document doc = DocumentFactory.getInstance().createDocument();
			Element root = doc.addElement("SimpleLogViewer");			
			// Write the SL clustering result
			root.add(_sl.toDOM());
			
			// Write the encoded log texts
			String base64Text = Base64Coder.encodeString(_logTextArea.getText());
			root.addElement("logs").addText(base64Text);
			
			// Write the current summarize level
			root.addElement("summarizelevel").addText(_numEvents+"");
			
			// Write the DOM to the file
			FileOutputStream fos = new FileOutputStream(filename);
			OutputFormat format = OutputFormat.createPrettyPrint();
			XMLWriter writer = new XMLWriter(fos, format);
			writer.write(doc);
			writer.close();
			this.setCursor(Cursor.getDefaultCursor());
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	private void startCreatingEvents() {
		try {
			this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
			// Create the log parser
			LogTreeParser parser = null;
			int parserChoice = _parserChooseCombox.getSelectedIndex();
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
			
			String loadStartPosStr = _loadStartPosCombox.getSelectedItem().toString();
			int loadStartPos = Integer.parseInt(loadStartPosStr);
			String loadLengthStr = _loadLengthCombox.getSelectedItem().toString();
			int loadLength;
			if (loadLengthStr.equalsIgnoreCase("ALL")) {
				loadLength = -1;
			}
			else {
				loadLength = Integer.parseInt(loadLengthStr);
			}
			
			_logList = parser.parse(new BufferedReader(
					new FileReader(_curFileName)), loadStartPos, loadLength);
			_logMsgList = parser.parseForPlain(new BufferedReader(
					new FileReader(_curFileName)), true, loadStartPos, loadLength);
			
			// Create the clustering algorithm
			TreeSimilarity simFunc =  new FastMsgTreeSimilarity();
			TreeSegDictBuilder simMatrixBuilder = new TreeSegDictBuilder(_logList);
			SymmetricMatrix simMatrix = simMatrixBuilder.build();
			_sl = new SingleLinkage(_logList, simFunc);
			_sl.setSimMatrix(simMatrix);
			_sl.build();
			
			// Retrieve the results						
			_numEventsSlider.setEnabled(true);
			int numClusters = _numEventsSlider.getValue();
			_numEvents = numClusters;
			List<LogElement> forest = new ArrayList<LogElement>();
			_sl.getClusterCentroids(_numEvents, forest);
			
//			int[] centers = _sl.getClusterCentroids(_summarizeLevel);
//			for (int i=0; i<centers.length; i++) {
//				System.out.println(i+" : "+_logMsgList.get(centers[i]));
//			}
			
			// Prepare for the visualization
			boolean bDispTime = _enableDispTimestampCheckBox.isSelected();
			_visForest = prepareLogForestForVis(forest, bDispTime);
			
			// Update the visualization panel
			// GROSSMAN _treeVizPanel.updateForest(_visForest);
	        updateComponentsEnableStatus();
			this.invalidate();
			this.setCursor(Cursor.getDefaultCursor());
		}catch(Exception e) {
			e.printStackTrace();
		}
	}
	
	/**
	 * Add the time-stamp as the root node of each log elements
	 * @param forest
	 * @return 
	 */
	private List<LogElement> prepareLogForestForVis(List<LogElement> forest, 
			boolean bDispTimestamp) {
		return forest;
//		if (!bDispTimestamp) {
//			return forest;
//		} else {
//			List<LogElement> newForest = new ArrayList<LogElement>(forest
//					.size());
//			// Add the time interval for each log message
//			for (int i = 0; i < forest.size(); i++) {
//				LogElement e = forest.get(i);
//				assert (e.getInstIndices() != null);
//				LogElement newRoot = null;
//				if (e.getContent() == null || e.getContent().length() == 0) {
//					newRoot = e;
//				} else {
//					newRoot = new LogElement();
//				}
//
//				if (e.getInstIndices() == null || e.getInstIndices().length == 1) { // A instance log element
//					Calendar time = e.getTimestamp();
//					newRoot.setContent(StringHelper.CalenderToString(time));
//					newRoot.setLabel(LogElemLabel.DATE);
//				} else { // A merged log element
//					Calendar startTime = null;
//					Calendar endTime = null;
//					int[] instIndices = e.getInstIndices();
//					for (int j = 0; j < instIndices.length; j++) {
//						LogElement instE = _logList.get(instIndices[j]);
//						Calendar time = instE.getTimestamp();
//						if (startTime == null || startTime.after(time)) {
//							startTime = time;
//						}
//						if (endTime == null || endTime.before(time)) {
//							endTime = time;
//						}
//					}
//					newRoot.setContent(StringHelper.CalenderToString(startTime)
//							+ " to " + StringHelper.CalenderToString(endTime));
//					newRoot.setLabel(LogElemLabel.DATE);
//				}
//				newRoot.setCanShortDisplay(false);
//				if (newRoot != e) { // new root is a new node
//					newRoot.addChild(e);
//				}
//				newForest.add(newRoot);
//			}
//			return newForest;
//		}
	}
	
	public void createClusteredEvents(List<ClusteredLogEvent> eventItems, 
			List<ClusteredLogEventType> eventTypes, int numEvent) {
		int[] clusters = _sl.getClusterCentroids(numEvent);
		for (int i=0; i<clusters.length; i++) {
			LogElement logE = _logList.get(clusters[i]);
			String msg = _logMsgList.get(clusters[i]);
			ClusteredLogEventType type = new ClusteredLogEventType(msg);
			eventTypes.add(type);
		}
		for (int i=0; i<_logList.size(); i++) {
			LogElement e = _logList.get(i);
			String msg = _logMsgList.get(i);
			int cluId = _sl.getClusterId(i, clusters);
			eventItems.add(new ClusteredLogEvent(e, msg, eventTypes.get(cluId)));
		}
	}
	
	public int getCurNumEvents() {
		return _numEvents;
	}
	
	private void openEventTimeLineDialog() {
		this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
		List<ClusteredLogEventType> eventTypes = new ArrayList<ClusteredLogEventType>();
		List<ClusteredLogEvent> eventItems = new ArrayList<ClusteredLogEvent>(_logList.size());
		createClusteredEvents(eventItems, eventTypes, _numEvents);
		_eventTimeLineDlg = new EventTimeLineDialog(this);
		Rectangle rect = this.getBounds();
		rect.x += 10;
		rect.y += rect.height/6;
		rect.height = rect.height*2/3;
		_eventTimeLineDlg.setBounds(rect);
		_eventTimeLineDlg.setVisible(true);
		this.setCursor(Cursor.getDefaultCursor());
	}
	
	private void updateEventTimeLineDialog() {
		this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
		_eventTimeLineDlg.updateEvents(_numEvents);
		this.setCursor(Cursor.getDefaultCursor());
	}
	
	
	private void openEventHistogramDialog() {
		this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
		List<ClusteredLogEventType> eventTypes = new ArrayList<ClusteredLogEventType>();
		List<ClusteredLogEvent> eventItems = new ArrayList<ClusteredLogEvent>(_logList.size());
		createClusteredEvents(eventItems, eventTypes, _numEvents);
		_eventHistDlg = new EventHistogramDialog(eventItems, eventTypes);
		Rectangle rect = this.getBounds();
		rect.y += 10;
		rect.height = rect.height*2/3;
		_eventHistDlg.setBounds(rect);
		_eventHistDlg.setVisible(true);
		this.setCursor(Cursor.getDefaultCursor());
	}
	
	private void updateEventHistogramDialog() {
		this.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
		List<ClusteredLogEventType> eventTypes = new ArrayList<ClusteredLogEventType>();
		List<ClusteredLogEvent> eventItems = new ArrayList<ClusteredLogEvent>(_logList.size());
		createClusteredEvents(eventItems, eventTypes, _numEvents);
		_eventHistDlg.updateEvents(eventItems, eventTypes);
		this.setCursor(Cursor.getDefaultCursor());
	}
	
	private void updateComponentsEnableStatus() {
		boolean enable;
		
		enable = !(_logList == null || _visForest == null);
		_enableDispTimestampCheckBox.setEnabled(enable);
		_enableFullDispVertexCheckBox.setEnabled(enable);
		_showEventTimeLineButton.setEnabled(enable);
		_showEventHistButton.setEnabled(enable);
		_numEventsSlider.setEnabled(enable);
		_treeVizPanel.setEnabled(enable);
		
		enable =  _curFileName != null && _curFileName.length() > 0 && 
				_logTextArea.getText() != null && _logTextArea.getText().length() >= 1;
		_logTextArea.setEnabled(enable);
		_startCreatingEventsButton.setEnabled(enable);
		_parserChooseCombox.setEnabled(enable);
	}
	

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		try {
			UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
			SimpleLogViewer frame = new SimpleLogViewer();        
	        frame.pack();
	        frame.setVisible(true);
		}catch(Exception e) {
			e.printStackTrace();
		}
	}


}
