package core;

import org.dom4j.Element;

public interface XMLPersistent {
	
	Element toDOM() throws Exception;
	
	void fromDOM(Element e) throws Exception;

}
