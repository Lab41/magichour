package loginsight.gui.visualization;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.geom.Ellipse2D;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.swing.JLabel;
import javax.swing.JPanel;

import loginsight.core.EventItem;
import loginsight.core.EventType;
import loginsight.helper.StringHelper;

import org.jfree.chart.ChartMouseEvent;
import org.jfree.chart.ChartMouseListener;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.axis.SymbolAxis;
import org.jfree.chart.entity.ChartEntity;
import org.jfree.chart.entity.XYItemEntity;
import org.jfree.chart.labels.CustomXYToolTipGenerator;
import org.jfree.chart.labels.XYItemLabelGenerator;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.StandardXYItemRenderer;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

@SuppressWarnings("serial")
public class EventTimeLinePanel extends JPanel implements ChartMouseListener{
	
	
	final static int maxAxisTickLabelLen = 15;

    /** The series. */
    private EventSeries series;
    
    XYSeriesCollection data;
    NumberAxis domainAxis;
    NumberAxis rangeAxis;
    StandardXYItemRenderer renderer;
    XYPlot plot;
    JFreeChart chart;
    ChartPanel chartPanel;
    int curSelectEventIndex = -1;
    JLabel curMsgLabel; 
    XYSeries curEventItemSeries;
    List<EventTimeLinePanelActionListener> actionlisterners = new ArrayList<EventTimeLinePanelActionListener>(); 
    

    /**
     * A demonstration application showing a series with different shape attributes per item.
     *
     * @param title  the frame title.
     */
    public EventTimeLinePanel(Collection<? extends EventItem> eventItems, 
    		Collection<? extends EventType> eventTypes) {
    	
    	chartPanel = buildChartPanel(eventItems, eventTypes);
    	chartPanel.addChartMouseListener(this);
        this.setLayout(new BorderLayout());
        this.add(chartPanel, BorderLayout.CENTER);
        
        JPanel southPanel = new JPanel();
        southPanel.setLayout(new BorderLayout());
        JPanel curMsgPanel = new JPanel();
        
        curMsgLabel = new JLabel("");
        curMsgLabel.setForeground(Color.black);
        curMsgLabel.setBackground(new Color(255,255,204));
        curMsgPanel.setMinimumSize(new Dimension(0, 30));
        curMsgPanel.setBackground(new Color(255,255,204));
        curMsgPanel.add(curMsgLabel, BorderLayout.CENTER);
        southPanel.add(curMsgPanel, BorderLayout.EAST);
        this.add(southPanel, BorderLayout.SOUTH);
    }
    
    public void updateEvents(Collection<? extends EventItem> eventItems, 
    		Collection<? extends EventType> eventTypes) {
    	chartPanel.setVisible(false);
    	this.remove(chartPanel);
    	chartPanel = buildChartPanel(eventItems, eventTypes);
    	chartPanel.addChartMouseListener(this);
        this.add(chartPanel, BorderLayout.CENTER);
        this.invalidate();
    }
    
    public void updateCurSelEvent(int eventIndex) {
    	curSelectEventIndex = eventIndex;
    	if (curSelectEventIndex >= 0) {
    		XYSeries itemSeriesOfEvent = series.getIndividualEventSeries(eventIndex);
    		curEventItemSeries.clear();
    		for (int i = 0; i<itemSeriesOfEvent.getItemCount(); i++) {
    			curEventItemSeries.add(itemSeriesOfEvent.getDataItem(i));
    		}
    		this.chart.fireChartChanged();
    		this.chartPanel.invalidate();
    	}
    }
    
    public void addActionListener(EventTimeLinePanelActionListener listener) {
    	this.actionlisterners.add(listener);
    }
    
    private ChartPanel buildChartPanel(Collection<? extends EventItem> eventItems, 
    		Collection<? extends EventType> eventTypes) {
    	series = new EventSeries(eventItems, eventTypes);
    	curEventItemSeries = new XYSeries("Event Time Line", false, true);
        data = new XYSeriesCollection(series); // For series 0
        data.addSeries(curEventItemSeries); // For series 1
        data.addSeries(series); // For series 2
        
        domainAxis = new NumberAxis("Time");
        rangeAxis = new SymbolAxis("", series.getYAxisLabels());
        rangeAxis.setTickLabelFont(new Font("Times", Font.BOLD, 11));
        // rangeAxis.setLabelFont(new Font("Serif", Font.BOLD, 24));
        CustomXYToolTipGenerator ttg = new CustomXYToolTipGenerator();
        ttg.addToolTipSeries(series.getItemToolTips());
        
        renderer = new StandardXYItemRenderer(StandardXYItemRenderer.SHAPES, ttg);        
        renderer.setSeriesPaint(0, Color.black);
        renderer.setSeriesShape(0, new Ellipse2D.Double(0,0, 6.8, 6.8));
        renderer.setSeriesShapesFilled(0, false);
        // Series 1 is for items of current selected event
        renderer.setSeriesPaint(1, Color.yellow);
        renderer.setSeriesShape(1, new Ellipse2D.Double(0.2,0.2, 6.5, 6.5));
        renderer.setSeriesShapesFilled(1, true);
        // Series 2 is for all items
        renderer.setSeriesPaint(2, Color.red);
        renderer.setSeriesShape(2, new Ellipse2D.Double(0.2,0.2, 6.5, 6.5));        
        renderer.setSeriesShapesFilled(2, true);
        
        EventItemLabelGenerator itemLabelGen = new EventItemLabelGenerator(series.getItemToolTips());
        renderer.setSeriesItemLabelGenerator(2, itemLabelGen);

        plot = new XYPlot(data, domainAxis, rangeAxis, renderer);
        // plot.setSeriesRenderingOrder(SeriesRenderingOrder.FORWARD);
        chart = new JFreeChart(plot);
        chart.removeLegend();
        return new ChartPanel(chart);
        //chartPanel.setPreferredSize(new java.awt.Dimension(600, 380));
    }
    
    
    
    @SuppressWarnings("serial")
	class EventSeries extends XYSeries {
    	
    	final static int width = 5;
    	final static int height = 5;
    	final static int margin = 1;
    	
    	Map<EventType, Integer> eventTypeMap = null;
    	List<EventItem> _items = null;
    	Map<String, Integer> _msgEventMap = null;
    	XYSeries[] individualEventSeries = null;
    	
		public EventSeries(Collection<? extends EventItem> items,
				Collection<? extends EventType> eventTypes) {
			super("Event Time Line", false, true);
			// TODO Auto-generated constructor stub
			// Create the event type map
			if (items == null || eventTypes == null) {
				return;
			}
			
			_msgEventMap = new HashMap<String, Integer>();
			eventTypeMap = new HashMap<EventType, Integer>();
			Iterator<? extends EventType> eventTypeIt = eventTypes.iterator();
			int eventTypeIndex = 0;
			while(eventTypeIt.hasNext()) {
				eventTypeMap.put(eventTypeIt.next(), eventTypeIndex);
				eventTypeIndex++;
			}
			
			individualEventSeries = new XYSeries[eventTypeIndex];
			for (int i=0; i<individualEventSeries.length; i++) {
				individualEventSeries[i] = new XYSeries("Event Time Line", false, true);
			}
			// Add all event items
			_items = new ArrayList<EventItem>(items.size());
			Iterator<? extends EventItem> itemIt = items.iterator();
			while(itemIt.hasNext()) {
				EventItem item = itemIt.next();
				EventType type = item.getType();
				_items.add(item);
				
				Integer eventIndex = eventTypeMap.get(type);
				assert(eventIndex != null);
				_msgEventMap.put(item.getDescription(), eventIndex);
				
				Calendar time = item.getStartTime();			
				double x = time.get(Calendar.SECOND); 
				double y = eventIndex*(height+margin);
				y = eventIndex;
				//y = 1;
				this.add(x, y);
				individualEventSeries[eventIndex].add(x, y);
			}
		}
		
		public int getEventIndex(String item) {
			Integer eventIndex = _msgEventMap.get(item);
			if (eventIndex == null)
				return -1;
			else
				return eventIndex;
		}
		
		public XYSeries getIndividualEventSeries(int eventIndex) {
			return individualEventSeries[eventIndex];
		}
		
		public String[] getYAxisLabels() {
			if (eventTypeMap == null) {
				return new String[]{};
			}
			int numLabel = eventTypeMap.size();
			String[] labels = new String[numLabel];			
			Iterator<Map.Entry<EventType, Integer>> it = eventTypeMap.entrySet().iterator();
			while(it.hasNext()) {
				Map.Entry<EventType, Integer> entry = it.next();
				String label = entry.getKey().getDescription();
				// compress the length of the message
				if (label.length() > maxAxisTickLabelLen) {
					label = StringHelper.cutStringForShort(label, maxAxisTickLabelLen);
				}
				labels[entry.getValue()] = label;
			}
			return labels;
		}
		
		public List<String> getItemToolTips() {
			List<String> tips = new ArrayList<String>(_items.size());
			for (int i=0; i<_items.size(); i++) {
				tips.add(_items.get(i).getDescription());
			}
			return tips;
		}
    }
    
    
    class EventItemLabelGenerator implements XYItemLabelGenerator {
    	
    	List<String> _labels = null;
    	
    	public EventItemLabelGenerator(List<String >labels) {
    		_labels = labels;
    	}
    	
		public String generateLabel(XYDataset dataset, int series, int item) {
			// TODO Auto-generated method stub
			return _labels.get(item);
		}
    	
    }
    
    public static interface EventTimeLinePanelActionListener {
    	
    	void mouseMoveOnItem(String item);
    	void mouseClickItem(String item);
    }


	public void chartMouseClicked(ChartMouseEvent event) {
		// TODO Auto-generated method stub
		if (event == null)
			return;
		int clickCount = event.getTrigger().getClickCount();
		if (clickCount >= 1) {			
			ChartEntity entity = event.getEntity();
			System.out.println(entity.getClass().getName());
			if (entity instanceof XYItemEntity) {
				XYItemEntity item = (XYItemEntity)event.getEntity();
				String itemDesc = item.getToolTipText();
				int eventIndex = series.getEventIndex(itemDesc);
				if (eventIndex >= 0) {
					this.updateCurSelEvent(eventIndex);
				}
				System.out.println("Clicked "+item.getItem()+ " : "+item.getToolTipText());			
			}
		}
	}


	public void chartMouseMoved(ChartMouseEvent event) {
		// TODO Auto-generated method stub
		if (event == null)
			return;
		ChartEntity entity = event.getEntity();
		if (entity instanceof XYItemEntity) {
			XYItemEntity item = (XYItemEntity)event.getEntity();
			String tooltip = item.getToolTipText();
			if (tooltip == null) {
				return;
			}
			tooltip = tooltip.trim();
			if (tooltip.length() == 0) {
				return;
			}
			fireMouseMoveItemEvent(tooltip);
		}
	}
	
	public void fireMouseMoveItemEvent(String item) {
		for (int i=0; i<this.actionlisterners.size(); i++) {
			actionlisterners.get(i).mouseMoveOnItem(item);
		}
	}

}
