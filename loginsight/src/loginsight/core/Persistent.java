package loginsight.core;

import java.io.InputStream;
import java.io.OutputStream;

public interface Persistent {
	
	void writeObject(OutputStream os);
	
	void readObject(InputStream is);

}
