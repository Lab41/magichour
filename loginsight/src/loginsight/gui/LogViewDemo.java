package loginsight.gui;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.general.DatasetUtilities;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;

public class LogViewDemo extends ApplicationFrame  {
	
	/** A constant for the number of items in the sample dataset. */
    private static final int COUNT = 500000;

    /** The data. */
    private float[][] data = new float[2][COUNT];
	
	public LogViewDemo(final String title) {

		super(title);
		CategoryDataset dataset = createCategoryDataset();
		JFreeChart chart = createChart(dataset);
		ChartPanel chartPanel = new ChartPanel(chart);
		chartPanel.setPreferredSize(new java.awt.Dimension(500, 270));
		setContentPane(chartPanel);
	}
	
	/**
     * Populates the data array with random values.
     */
    private void populateData() {

        for (int i = 0; i < this.data[0].length; i++) {
            final float x = (float) i + 100000;
            this.data[0][i] = x;
            this.data[1][i] = 100000 + (float) Math.random() * COUNT;
        }

    }
    
    /**
     * Creates a sample chart.
     * 
     * @param dataset  the dataset for the chart.
     * 
     * @return a sample chart.
     */
    private JFreeChart createChart(CategoryDataset dataset) {

        JFreeChart chart = ChartFactory.createStackedBarChart(
            "Stacked Bar Chart Demo 1",  // chart title
            "Category",                  // domain axis label
            "Value",                     // range axis label
            dataset,                     // data
            PlotOrientation.VERTICAL,    // the plot orientation
            true,                        // legend
            true,                        // tooltips
            false                        // urls
        );
        return chart;
        
    }
    
    public static CategoryDataset createCategoryDataset() {

        double[][] data = new double[][]
            {{10.0, 4.0, 15.0, 14.0},
             {6.0, 17.0, -12.0, 7.0},
             {-3.0, 7.0, 11.0, -10.0}};

        return DatasetUtilities.createCategoryDataset("Series ", "Category ", data);

    }




    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(final String[] args) {

    	LogViewDemo demo = new LogViewDemo("Stacked Bar Chart Demo 1");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}
