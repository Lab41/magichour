package loginsight.gui.simpleviewer;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.util.ArrayList;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JSlider;
import javax.swing.SwingConstants;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import loginsight.clustering.ClusteredLogEvent;
import loginsight.clustering.ClusteredLogEventType;
import loginsight.gui.visualization.EventTimeLinePanel;
import loginsight.gui.visualization.EventTimeLinePanel.EventTimeLinePanelActionListener;

public class EventTimeLineDialog extends JFrame implements ChangeListener, EventTimeLinePanelActionListener{
	
	SimpleLogViewer _mainFrame = null;
	EventTimeLinePanel _eventTimeLinePanel = null;
	JLabel  _curItemLabel;
	JSlider _eventLevelSlider;
	int _numEvents = 0;
	
	public EventTimeLineDialog(SimpleLogViewer mainFrame) {
		// TODO Auto-generated constructor stub
		super("Event Time Line");
		_mainFrame = mainFrame;
		List<ClusteredLogEventType> eventTypes = new ArrayList<ClusteredLogEventType>();
		List<ClusteredLogEvent> eventItems = new ArrayList<ClusteredLogEvent>();
		_numEvents = _mainFrame.getCurNumEvents();
		_mainFrame.createClusteredEvents(eventItems, eventTypes, _numEvents);		
		_eventTimeLinePanel = new EventTimeLinePanel(eventItems, eventTypes);
		_eventTimeLinePanel.addActionListener(this);
		this.setLayout(new BorderLayout());
		this.setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		this.getContentPane().add(_eventTimeLinePanel, BorderLayout.CENTER);
		
		_eventLevelSlider = new JSlider(SwingConstants.VERTICAL, 0, 100, 10);
		_eventLevelSlider.addChangeListener(this);
		_eventLevelSlider.setPaintTicks(true);
		_eventLevelSlider.setPaintLabels(true);
		_eventLevelSlider.setMajorTickSpacing(5);
		_eventLevelSlider.setMinorTickSpacing(5);
		this.getContentPane().add(_eventLevelSlider, BorderLayout.WEST);
		
		JPanel southPanel = new JPanel();
        southPanel.setLayout(new BorderLayout());
        JPanel curItemPanel = new JPanel();
        
        _curItemLabel = new JLabel("");
        _curItemLabel.setForeground(Color.black);
        _curItemLabel.setBackground(new Color(255,255,204));
        curItemPanel.setMinimumSize(new Dimension(0, 30));
        curItemPanel.setBackground(new Color(255,255,204));
        curItemPanel.add(_curItemLabel, BorderLayout.CENTER);
        southPanel.add(curItemPanel, BorderLayout.EAST);
        this.getContentPane().add(southPanel, BorderLayout.SOUTH);
	}
	
	
	public void updateEvents(int numEvents) {
		List<ClusteredLogEventType> eventTypes = new ArrayList<ClusteredLogEventType>();
		List<ClusteredLogEvent> eventItems = new ArrayList<ClusteredLogEvent>();
		_mainFrame.createClusteredEvents(eventItems, eventTypes, numEvents);		
		_eventTimeLinePanel.updateEvents(eventItems, eventTypes);
		_numEvents = numEvents;
	}


	public void stateChanged(ChangeEvent e) {
		// TODO Auto-generated method stub
		if (e.getSource() == _eventLevelSlider) {
			int numClusters = _eventLevelSlider.getValue();
			updateEvents(numClusters);
		}
	}


	public void mouseClickItem(String item) {
		// TODO Auto-generated method stub
		
	}


	public void mouseMoveOnItem(String item) {
		// TODO Auto-generated method stub
		_curItemLabel.setText(item);
	}
	
	

}
