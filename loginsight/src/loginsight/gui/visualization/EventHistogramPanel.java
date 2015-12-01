package loginsight.gui.visualization;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Paint;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import javax.swing.JPanel;

import loginsight.core.EventItem;
import loginsight.core.EventType;
import loginsight.helper.StringHelper;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.CategoryLabelPositions;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.labels.CategoryToolTipGenerator;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.category.BarRenderer;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.category.DefaultCategoryDataset;

public class EventHistogramPanel extends JPanel {
	
	
	ChartPanel chartPanel;
	final static int maxAxisTickLabelLen = 14;
	Map<EventType, Integer> histMap = null;
	EventToolTipsGenerator tooltips = null;
	
	
	public EventHistogramPanel(Collection<? extends EventItem> eventItems,
			Collection<? extends EventType> eventTypes) {
		chartPanel = createChartPanel(eventItems, eventTypes);
        this.setLayout(new BorderLayout());
        this.add(chartPanel, BorderLayout.CENTER);
	}
	
	
	public void updateEvents(Collection<? extends EventItem> eventItems,
			Collection<? extends EventType> eventTypes) {
		chartPanel.setVisible(false);
		this.remove(chartPanel);
		chartPanel = createChartPanel(eventItems, eventTypes);
		this.add(chartPanel, BorderLayout.CENTER);
		this.invalidate();
	}
	
	private ChartPanel createChartPanel(Collection<? extends EventItem> eventItems,
			Collection<? extends EventType> eventTypes) {
		CategoryDataset dataset = createDataset(eventItems, eventTypes);
        JFreeChart chart = createChart(dataset);
        return new ChartPanel(chart);
	}
		
	/**
     * Returns a sample dataset.
     * 
     * @return The dataset.
     */
    private CategoryDataset createDataset(Collection<? extends EventItem> eventItems,
			Collection<? extends EventType> eventTypes) {
        
        // column keys...
        final String category1 = "Events";
        
        // create the dataset...
        
        histMap = new HashMap<EventType, Integer>();
        Iterator<? extends EventItem> eventIt = eventItems.iterator();
        while(eventIt.hasNext()) {
        	EventItem event = eventIt.next();
        	EventType type = event.getType();
        	Integer count = histMap.get(type);
        	if (count == null) 
        		count = 0;
        	histMap.put(type, count+1);
        }
        
        tooltips = new EventToolTipsGenerator();
        DefaultCategoryDataset dataset = new DefaultCategoryDataset();
        Iterator<Map.Entry<EventType, Integer>> entryIt = histMap.entrySet().iterator();
        int eventNo = 0;
        while(entryIt.hasNext()) {
        	Map.Entry<EventType, Integer> entry = entryIt.next();
        	int count = entry.getValue();
        	String label = entry.getKey().getDescription();
        	tooltips.add(label, count);
        	System.out.println(""+eventNo+" : " +label);
        	if (label.length() > maxAxisTickLabelLen) {
        		label = StringHelper.cutStringForShort(label, 
        				maxAxisTickLabelLen);
        	}
        	dataset.addValue(count, category1, eventNo+":"+label);
        	eventNo++;
        }
        
        return dataset;
    }
    
    /**
     * Creates a sample chart.
     * 
     * @param dataset  the dataset.
     * 
     * @return The chart.
     */
    private JFreeChart createChart(final CategoryDataset dataset) {
        
        // create the chart...
        final JFreeChart chart = ChartFactory.createBarChart(
            "Event Histogram",         // chart title
            "Event",               // domain axis label
            "Count",                  // range axis label
            dataset,                  // data
            PlotOrientation.HORIZONTAL, // orientation
            true,                     // include legend
            true,                     // tooltips?
            false                     // URLs?
        );

        // NOW DO SOME OPTIONAL CUSTOMISATION OF THE CHART...

        // set the background color for the chart...
        chart.setBackgroundPaint(Color.white);

        // get a reference to the plot for further customisation...
        final CategoryPlot plot = chart.getCategoryPlot();
        plot.setBackgroundPaint(Color.lightGray);
        plot.setDomainGridlinePaint(Color.white);
        plot.setRangeGridlinePaint(Color.white);

        // set the range axis to display integers only...
        final NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());
        

        // disable bar outlines...
        CustomRenderer renderer = new CustomRenderer(histMap.size());
        renderer.setSeriesToolTipGenerator(0, tooltips);
        plot.setRenderer(renderer);
        

        final CategoryAxis domainAxis = plot.getDomainAxis();
        domainAxis.setCategoryLabelPositions(
            CategoryLabelPositions.createUpRotationLabelPositions(Math.PI / 6.0)
        );
        // OPTIONAL CUSTOMISATION COMPLETED.
        
        return chart;
    }
    
    /**
     * A custom renderer that returns a different color for each item in a single series.
     */
    static class CustomRenderer extends BarRenderer {

        /** The colors. */
        private static Paint[] colors;
        
        static {
        	colors = new Color[255];
        	for (int i=0; i<255; i++) {
        		colors[i] = new Color(i,(i+128)%255, (255-i)%255);
        	}
        }
        
        private int colorScale = 1;

        /**
         * Creates a new renderer.
         *
         * @param colors  the colors.
         */
        public CustomRenderer(int maxCol) {
        	this.colorScale = colors.length / maxCol;
        }

        /**
         * Returns the paint for an item.  Overrides the default behaviour inherited from
         * AbstractSeriesRenderer.
         *
         * @param row  the series.
         * @param column  the category.
         *
         * @return The item color.
         */
        @Override
		public Paint getItemPaint(final int row, final int column) {
            return CustomRenderer.colors[(column*colorScale)% CustomRenderer.colors.length];
        }
    }

    
    
    class EventToolTipsGenerator  implements CategoryToolTipGenerator {
    	
    	List<String> tooltips = new ArrayList<String>();
    	List<Double> values = new ArrayList<Double>();
    	
    	public EventToolTipsGenerator() {
    		
    	}
    	
    	public void add(String label, double val) {
    		tooltips.add(label);
    		values.add(val);
    	}

		public String generateToolTip(CategoryDataset dataset, int row,
				int column) {
			// TODO Auto-generated method stub			
			return tooltips.get(column);
		}
    	
    }

}
