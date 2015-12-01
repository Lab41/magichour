package loginsight.gui;

import java.util.Calendar;
import java.util.List;

import loginsight.logtree.LogElement;

import org.jfree.data.general.DatasetChangeEvent;
import org.jfree.data.general.DatasetChangeListener;
import org.jfree.data.xy.AbstractXYDataset;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class LogSeriesDataset extends AbstractXYDataset implements
		XYDataset, DatasetChangeListener {
	
	private XYDataset _underlying;
    private long _curTime = 0;
    private long _timeWindowLen = 1000;
    private List<LogElement> _logList = null;
    private int _panel_width = 800;
    private int _box_width = 50;
    private int _box_height = 50;
    private int _box_margin = 10;

	public LogSeriesDataset(List<LogElement> logList) {
		// TODO Auto-generated constructor stub
		_logList = logList;
		transformDataset();
        this._underlying.addChangeListener(this);
        this._curTime = 0; 
	}
	
	private void transformDataset() {
		XYSeries series = new XYSeries("Messages");
		long y = 0;
		long lastTime = -1;
		long boxTimeUnit = _timeWindowLen*_box_width / _panel_width;
		for (int i=0; i<_logList.size(); i++) {
			LogElement e = _logList.get(i);
			Calendar cal = e.getTimestamp();
			long time = cal.getTimeInMillis();
			if (lastTime < 0) { // The first timestamp
				lastTime = time;
				_curTime = time;
			}
			else {
				if (Math.abs(time - lastTime) < boxTimeUnit+_box_margin) {
					y += _box_height+_box_margin;
				}
			}
			series.add(time, y);
		}
		
        series.add(-20.0, 20.0);
        series.add(40.0, 25.0);
        series.add(55.0, 50.0);
        series.add(70.0, 65.0);
        series.add(270.0, 65.0);
        series.add(570.0, 55.0);
		this._underlying = new XYSeriesCollection(series);
	}
	
	/**
     * Returns the current translation factor.
     *
     * @return The translation factor.
     */
    public double getTranslate() {
        return this._curTime;
    }
   
    /**
     * Sets the translation factor.
     *
     * @param t  the translation factor.
     */
    public void setTranslate(long t) {
        this._curTime = t;
        fireDatasetChanged();
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
          return this._underlying.getXValue(series, item) + _curTime;
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

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

}
