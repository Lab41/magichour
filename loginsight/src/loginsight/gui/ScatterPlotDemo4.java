package loginsight.gui;

import java.awt.BorderLayout;

import javax.swing.BorderFactory;
import javax.swing.JPanel;
import javax.swing.JSlider;
import javax.swing.border.Border;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;


public class ScatterPlotDemo4 extends ApplicationFrame  implements ChangeListener{

	JSlider slider = null;
	 /**
     * A demonstration application showing a scatter plot.
     *
     * @param title  the frame title.
     */
    public ScatterPlotDemo4(String title) {

        super(title);
        XYSeries series = new XYSeries("Average Weight");
        series.add(-20.0, 20.0);
        series.add(40.0, 25.0);
        series.add(55.0, 50.0);
        series.add(70.0, 65.0);
        series.add(270.0, 65.0);
        series.add(570.0, 55.0);
        XYDataset data = new XYSeriesCollection(series);
        JFreeChart chart = ChartFactory.createScatterPlot(
            "Scatter Plot Demo",
            "X", 
            "Y", 
            data, 
            PlotOrientation.VERTICAL,
            true, 
            true, 
            false
        );
        XYPlot plot = chart.getXYPlot();
        LogElemRenderer render = new LogElemRenderer();
        render.setDotWidth(25);
        render.setDotHeight(25);
        plot.setRenderer(render);
        plot.setDomainCrosshairVisible(true);
        plot.setRangeCrosshairVisible(true);

        NumberAxis domainAxis = (NumberAxis) plot.getDomainAxis();
        domainAxis.setAutoRangeIncludesZero(false);

        ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new java.awt.Dimension(800, 470));
        
        Border border = BorderFactory.createCompoundBorder(
                BorderFactory.createEmptyBorder(4, 4, 4, 4),
                BorderFactory.createEtchedBorder()
            );
        chartPanel.setBorder(border);
        add(chartPanel);

		JPanel dashboard = new JPanel(new BorderLayout());
		dashboard.setBorder(BorderFactory.createEmptyBorder(0, 4, 4, 4));
		// make the slider units "minutes"
		slider = new JSlider(-200, 200, 0);
		slider.setPaintLabels(true);
		slider.setMajorTickSpacing(50);
		slider.setPaintTicks(true);
		slider.addChangeListener(this);
		dashboard.add(slider);
		add(dashboard, BorderLayout.SOUTH);

        //setContentPane(chartPanel);

    }
    
    /**
     * Handles a state change event.
     *
     * @param event  the event.
     */
    public void stateChanged(ChangeEvent event) {
        int value = this.slider.getValue();
        System.out.println(""+value);
        // value is in minutes
        //this.dataset.setTranslate(value * 60 * 1000.0);
    } 

    // ****************************************************************************
    // * JFREECHART DEVELOPER GUIDE                                               *
    // * The JFreeChart Developer Guide, written by David Gilbert, is available   *
    // * to purchase from Object Refinery Limited:                                *
    // *                                                                          *
    // * http://www.object-refinery.com/jfreechart/guide.html                     *
    // *                                                                          *
    // * Sales are used to provide funding for the JFreeChart project - please    * 
    // * support us so that we can continue developing free software.             *
    // ****************************************************************************
    
    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {

        ScatterPlotDemo4 demo = new ScatterPlotDemo4("Scatter Plot Demo 4");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}
