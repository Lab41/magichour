package loginsight.gui.visualization;

import org.jfree.data.general.DatasetChangeEvent;
import org.jfree.data.general.DatasetChangeListener;
import org.jfree.data.xy.AbstractXYDataset;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class ClusterDataset extends AbstractXYDataset implements XYDataset,
		DatasetChangeListener {
	
	protected XYDataset _underlying;
	protected String[] _dataLabels;
    protected int _panel_width = 800;
    protected int _box_width = 50;
    protected int _box_height = 50;

	public ClusterDataset(double[][] values, String[] labels, String name) {
		// TODO Auto-generated constructor stub
		XYSeries series = new XYSeries(name);
		for (int i=0; i<values.length; i++) {
			series.add(values[i][0], values[i][1]);
		}
		_dataLabels = new String[labels.length];
		System.arraycopy(labels, 0, _dataLabels, 0, labels.length);
        _underlying = new XYSeriesCollection(series);
	}

	@Override
	public int getSeriesCount() {
		// TODO Auto-generated method stub
		return this._underlying.getSeriesCount();
	}

	@Override
	public Comparable getSeriesKey(int series) {
		// TODO Auto-generated method stub
		return this._underlying.getSeriesKey(series);
	}

	public int getItemCount(int series) {
		// TODO Auto-generated method stub
		return this._underlying.getItemCount(series);
	}
	
	@Override
	public double getXValue(int series, int item) {
          return this._underlying.getXValue(series, item);
    } 

	public Number getX(int series, int item) {
		// TODO Auto-generated method stub
		return new Double(getXValue(series, item)); 
	}
	
	@Override
	public double getYValue(int series, int item) {
        return this._underlying.getYValue(series, item);
    } 

	public Number getY(int series, int item) {
		// TODO Auto-generated method stub
		return new Double(getYValue(series, item)); 
	}

	public void datasetChanged(DatasetChangeEvent event) {
		// TODO Auto-generated method stub
		this.fireDatasetChanged(); 
	}
	
	public String getLabel(int item) {
		return _dataLabels[item];
	}
	
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

}
