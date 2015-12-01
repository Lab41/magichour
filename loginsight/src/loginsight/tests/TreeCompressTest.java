package loginsight.tests;

import loginsight.core.TreeMerger;
import loginsight.logtree.LogElemLabel;
import loginsight.logtree.LogElement;

public class TreeCompressTest {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		LogElement e1 = new LogElement("A", LogElemLabel.ID);
		e1.addChild(new LogElement("B", LogElemLabel.ID));
		e1.addChild(new LogElement("C", LogElemLabel.ID));
		
		LogElement e2 = new LogElement("A", LogElemLabel.ID);
		LogElement b2 = new LogElement("B", LogElemLabel.ID);
		b2.addChild(new LogElement("x1", LogElemLabel.ID));
		b2.addChild(new LogElement("x2", LogElemLabel.ID));
		e2.addChild(b2);
		e2.addChild(new LogElement("D", LogElemLabel.ID));
		
		LogElement e3 = (LogElement)TreeMerger.build(e1, e2);
		e3.updateDepth(0);
		e3.print(System.out);
	}

}

