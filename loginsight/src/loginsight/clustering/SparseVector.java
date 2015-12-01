package loginsight.clustering;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;

public class SparseVector {
	private int _length = -1;
	private Map<Integer, Double> _valueMap = new HashMap<Integer, Double>();
	
	public SparseVector(double []v) {
		_length = v.length;
		for (int i=0; i<v.length; i++) {
			if (Double.compare(Math.abs(v[i]), 0) != 0) {
				_valueMap.put(i, v[i]);
			}
		}
	}
	
	public SparseVector() {
	}
	
	public void addValue(int d, double v) {
		_valueMap.put(d, v);
	}
	
	public double value(int d) {
		Double value = _valueMap.get(d);
		if (value == null)
			return 0;
		else
			return value;
	}
	
	public double dotProduct(SparseVector sv) {
		double s = 0;
		Iterator<Entry<Integer, Double>> it = _valueMap.entrySet().iterator();
		while(it.hasNext()) {
			Entry<Integer, Double> entry = it.next();
			s += entry.getValue() * sv.value(entry.getKey());
		}
		return s;
	}
	
	public SparseVector normalize() {
		double s = 0;
		Iterator<Entry<Integer, Double>> it = _valueMap.entrySet().iterator();
		while(it.hasNext()) {
			Entry<Integer, Double> entry = it.next();
			s += entry.getValue()* entry.getValue();
		}
		SparseVector normalizedV = new SparseVector();
		double r = Math.sqrt(s);
		it = _valueMap.entrySet().iterator();
		while(it.hasNext()) {
			Entry<Integer, Double> entry = it.next();
			normalizedV.addValue(entry.getKey(), entry.getValue()/r);
		}
		return normalizedV;
	}

}
