package loginsight.core;

public class SymmetricMatrix {
	
	double[] _elems = null;
	int _n = 0; // the data size
	
	public SymmetricMatrix(int n) {
		_elems = new double[n*(n+1)/2];
		_n = n;
	}
	
	public void set(int row, int col, double value) {
		int i = row > col ? row : col;
		int j = row+col-i;
		_elems[i*(i+1)/2+j] = value;
	}
	
	public double get(int row, int col) {
		int i = row > col ? row : col;
		int j = row+col-i;
		return _elems[i*(i+1)/2+j];
	}
	
	public int getSize() {
		return _n;
	}
	
}
