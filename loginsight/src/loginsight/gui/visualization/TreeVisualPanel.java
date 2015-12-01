package loginsight.gui.visualization;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.event.MouseEvent;
import java.awt.image.renderable.RenderContext;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.swing.JFrame;
import javax.swing.JPanel;

import org.apache.commons.collections4.Factory;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.functors.ChainedTransformer;
import org.apache.commons.collections4.functors.ConstantTransformer;

import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.Vertex;
import edu.uci.ics.jung.graph.decorators.EdgeShape;
import edu.uci.ics.jung.graph.decorators.ToStringLabeller;
import edu.uci.ics.jung.visualization.GraphMouseListener;
import edu.uci.ics.jung.visualization.GraphZoomScrollPane;
import edu.uci.ics.jung.visualization.VisualizationViewer;
import edu.uci.ics.jung.visualization.contrib.TreeLayout;
import edu.uci.ics.jung.visualization.control.DefaultModalGraphMouse;
import edu.uci.ics.jung.visualization.control.ModalGraphMouse;
import loginsight.core.TreeNode;
//import weka.classifiers.trees.REPTree.Tree;


@SuppressWarnings("serial")
public class TreeVisualPanel extends JPanel implements GraphMouseListener{

	
	// GROSSMAN
//	
//	  public class TreeVisualPanel extends JPanel implements GraphMouseListener<String>{
//
//	/**
//     * the graph
//     */
//    Forest<String,Integer> graph;
//    
//    Factory<DirectedGraph<String,Integer>> graphFactory = 
//    	new Factory<DirectedGraph<String,Integer>>() {
//
//			public DirectedGraph<String, Integer> create() {
//				return new DirectedSparseMultigraph<String,Integer>();
//			}
//		};
//			
//	Factory<Tree<String,Integer>> treeFactory =
//		new Factory<Tree<String,Integer>> () {
//
//		public Tree<String, Integer> create() {
//			return new DelegateTree<String,Integer>(graphFactory);
//		}
//	};
//	
//	Factory<Integer> edgeFactory = new Factory<Integer>() {
//		int i=0;
//		public Integer create() {
//			return i++;
//		}};
//    
//    Factory<String> vertexFactory = new Factory<String>() {
//    	int i=0;
//		public String create() {
//			return "V"+i++;
//		}};
//	
//		
//	List<? extends TreeNode> visTrees = null;
//	
//	Map<String, TreeNode> vertexLabelMap = new HashMap<String, TreeNode>();
//	
//	int vertexLabelNo = 0;
//
//    /**
//     * the visual component and renderer for the graph
//     */
//    VisualizationViewer<String,Integer> vv;
//    
//    String root;
//    
//    TreeLayout<String,Integer> treeLayout;
//    
//    GraphZoomScrollPane graphPanel;
//    
//    
//    static class VertexLabelTransfomer implements Transformer<String,String> {
//    	
//    	Map<String, TreeNode> _vertexLabelMap;
//    	
//    	int _maxCharPerLineInLabel = -1;
//    	
//    	public VertexLabelTransfomer(Map<String, TreeNode> vertexLabelMap, int maxCharPerLine) {
//    		this._vertexLabelMap = vertexLabelMap;
//    		this._maxCharPerLineInLabel = maxCharPerLine;
//    	}
//
//		public String transform(String input) {
//			// TODO Auto-generated method stub
//			TreeNode node = _vertexLabelMap.get(input);
//			String content = node.getContent().toString();
//			if (content == null || content.length() == 0)
//				content = "*";
//			if (node != null) {
//				if (node.canShortDisplay() && 
//						_maxCharPerLineInLabel != -1 &&
//						content.length() > _maxCharPerLineInLabel) {
//					content = content.substring(0, _maxCharPerLineInLabel);
//					content +="...";
//				}
//				content =  "<html><strong>"+content;
//			}
//			else
//				content = "null";
//			
//			if (node.isSlotNode()) {
//				content = "<html><FONT COLOR=\"#FF0000\"><strong>[...]";
//			}
//
//			return content;
//		}
//    }
//    
//    public TreeVisualPanel(List<? extends TreeNode> trees) {
//    	visTrees = trees;
//    	createVisualizationViewer(true);
//        graphPanel = new GraphZoomScrollPane(vv);
//        graphPanel.setPreferredSize(new Dimension(800, 370));
//        this.add(graphPanel);
////
////        final ScalingControl scaler = new CrossoverScalingControl();
////
////        JButton plus = new JButton("+");
////        plus.addActionListener(new ActionListener() {
////            public void actionPerformed(ActionEvent e) {
////                scaler.scale(vv, 1.1f, vv.getCenter());
////            }
////        });
////        JButton minus = new JButton("-");
////        minus.addActionListener(new ActionListener() {
////            public void actionPerformed(ActionEvent e) {
////                scaler.scale(vv, 1/1.1f, vv.getCenter());
////            }
////        });
////        
////        JPanel scaleGrid = new JPanel(new GridLayout(1,0));
////        scaleGrid.setBorder(BorderFactory.createTitledBorder("Zoom"));
////
////        JPanel controls = new JPanel();
////        scaleGrid.add(plus);
////        scaleGrid.add(minus);
////        controls.add(scaleGrid);
////
////        content.add(controls, BorderLayout.SOUTH);
//    }
//    
//    @Override
//    public void setPreferredSize(Dimension size) {
//    	graphPanel.setPreferredSize(size);
//    }
//    
//    public void updateForest(List<? extends TreeNode> trees) {
//    	visTrees = trees;
//    	createVisualizationViewer(true);    	
//        this.setVisible(false);
//        Dimension oldDimension = graphPanel.getPreferredSize();
//        this.remove(graphPanel);
//        graphPanel = new GraphZoomScrollPane(vv);
//        graphPanel.setPreferredSize(oldDimension);        
//        this.add(graphPanel);
//        this.setVisible(true);
//    }
//    
//    public void setEnableShortLabel(boolean bEnable) {
//    	createVisualizationViewer(false);    	
//        this.setVisible(false);
//        Dimension oldDimension = graphPanel.getPreferredSize();
//        this.remove(graphPanel);        
//        graphPanel = new GraphZoomScrollPane(vv);
//        graphPanel.setPreferredSize(oldDimension);        
//        this.add(graphPanel);
//        this.setVisible(true);
//    }
//        
//    private void createVisualizationViewer(boolean bEnableShortLabel) {
//    	graph = new DelegateForest<String,Integer>();
//        createForest(visTrees);
//        
//        treeLayout = new TreeLayout<String,Integer>(graph, 120);
//        vv =  new VisualizationViewer<String,Integer>(treeLayout, new Dimension(600,600));
//        vv.setBackground(Color.white);
//        vv.getRenderContext().setEdgeShapeTransformer(new EdgeShape.Line());
//        vv.getRenderContext().setVertexLabelTransformer(new ToStringLabeller());
//        // add a listener for ToolTips
//        vv.setVertexToolTipTransformer(new VertexLabelTransfomer(vertexLabelMap, -1));       
//        vv.getRenderContext().setArrowFillPaintTransformer(new ConstantTransformer(Color.lightGray));
//        // this class will provide both label drawing and vertex shapes
//        VertexLabelAsShapeRenderer<String,Integer> vlasr = new VertexLabelAsShapeRenderer<String,Integer>(vv.getRenderContext());
//        	
//        // customize the render context
//		if (bEnableShortLabel) {
//			vv.getRenderContext().setVertexLabelTransformer(
//			// this chains together Transformers so that the html tags
//					// are prepended to the toString method output
//					new ChainedTransformer<String, String>(new Transformer[] {
//							new ToStringLabeller<String>(),
//							new VertexLabelTransfomer(vertexLabelMap, 24) }));
//		} else {
//			vv.getRenderContext().setVertexLabelTransformer(
//			// this chains together Transformers so that the html tags
//					// are prepended to the toString method output
//					new ChainedTransformer<String, String>(new Transformer[] {
//							new ToStringLabeller<String>(),
//							new VertexLabelTransfomer(vertexLabelMap, -1) }));
//		}
//        RenderContext<String, Integer> rc = vv.getRenderContext();
//        rc.setVertexShapeTransformer(vlasr);
//        rc.setVertexLabelRenderer(new DefaultVertexLabelRenderer(Color.red));
//        rc.setEdgeDrawPaintTransformer(new ConstantTransformer(Color.black));
//        rc.setEdgeStrokeTransformer(new ConstantTransformer(new BasicStroke(2.5f)));
//        // customize the renderer
//        vv.getRenderer().setVertexRenderer(
//        		new GradientVertexRenderer<String,Integer>(new Color(149,202,228), Color.white, false));
//        vv.getRenderer().setVertexLabelRenderer(vlasr);
//        
//        final DefaultModalGraphMouse graphMouse = new DefaultModalGraphMouse();
//        vv.setGraphMouse(graphMouse);
//        //graphMouse.setMode(ModalGraphMouse.Mode.TRANSFORMING);
//        graphMouse.setMode(ModalGraphMouse.Mode.PICKING);
//        vv.addGraphMouseListener(this);
//    }
//       
//    private void createForest(List<? extends TreeNode> trees) {
//    	vertexLabelNo = 0;
//    	for (int i=0; i<trees.size(); i++) {
//    		TreeNode tree = trees.get(i);
//    		createTree(tree);
//    	}
//    }
//    
//    private void createTree(TreeNode root) {
//    	String parentVertex = createNewVertexLabel(root);
//    	graph.addVertex(parentVertex);
//    	createChildNodes(parentVertex, root);
//    }
//    
//    private void createChildNodes(String parentVertex, TreeNode parentNode) {
//    	for (int i=0; i<parentNode.getChildrenCount(); i++) {
//    		TreeNode childNode = parentNode.getChild(i);
//	    	String childVertex = createNewVertexLabel(childNode);
//	    	graph.addEdge(edgeFactory.create(), parentVertex, childVertex);
//	    	if (childNode.hasChild()) {
//	    		createChildNodes(childVertex, childNode);
//	    	}
//    	}
//    }
//    
//    private String createNewVertexLabel(TreeNode node) {
//    	String str = "V"+vertexLabelNo;
//    	vertexLabelMap.put(str, node);
//    	vertexLabelNo++;
//    	return str;
//    }
//    
//
//	public void graphClicked(String v, MouseEvent me) {
//		// TODO Auto-generated method stub
//		TreeNode node = vertexLabelMap.get(v);
//		System.out.println(node.getContent().toString());		
//	}
//
//	public void graphPressed(String v, MouseEvent me) {
//		// TODO Auto-generated method stub
//		
//	}
//
//	public void graphReleased(String v, MouseEvent me) {
//		// TODO Auto-generated method stub
//		
//	}
//
//
//    
//
//    /**
//     * a driver for this demo
//     */
//    public static void main(String[] args) {
//        JFrame frame = new JFrame();
//        Container content = frame.getContentPane();
//        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
//
//        content.add(new TreeVisualPanel(new java.util.ArrayList<TreeNode>()));
//        frame.pack();
//        frame.setVisible(true);
//    }

	@Override
	public void graphClicked(Vertex v, MouseEvent me) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void graphPressed(Vertex v, MouseEvent me) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void graphReleased(Vertex v, MouseEvent me) {
		// TODO Auto-generated method stub
		
	}

	

}
