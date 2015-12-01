package loginsight.gui.simpleviewer;

import java.awt.BorderLayout;
import java.util.Collection;

import javax.swing.JFrame;

import loginsight.core.EventItem;
import loginsight.core.EventType;
import loginsight.gui.visualization.EventHistogramPanel;

public class EventHistogramDialog extends JFrame {
	
	EventHistogramPanel _eventHistPanel = null;
	
	public EventHistogramDialog(Collection<? extends EventItem> eventItems,
			Collection<? extends EventType> eventTypes) {
		
		super("Event Histogram");
		
		_eventHistPanel = new EventHistogramPanel(eventItems, eventTypes);
		this.setLayout(new BorderLayout());
		this.setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		this.getContentPane().add(_eventHistPanel, BorderLayout.CENTER);		
	}
	
	public void updateEvents(Collection<? extends EventItem> eventItems,
			Collection<? extends EventType> eventTypes) {
		_eventHistPanel.updateEvents(eventItems, eventTypes);
	}

}
