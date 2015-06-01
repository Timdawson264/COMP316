import java.util.Arrays;
import java.util.Random;

/**
 * Simple class for approximate inference based on the Poker-game network.
 */
public class BayesNet
{

  /**
   * Inner class for representing a node in the network.
   */
  private class Node
  {

    // The name of the node
    private String name;

    // The parent nodes
    private Node[] parents;

    // The probabilities for the CPT
    private double[] probs;

    // The current value of the node
    public boolean value;

    /**
     * Initializes the node.
     */
    private Node( String n, Node[] pa, double[] pr )
    {
      name = n;
      parents = pa;
      probs = pr;
    }

    /**
     * Returns conditional probability of value "true" for the current node
     * based on the values of the parent nodes.
     *
     * @return The conditional probability of this node, given its parents.
     */
    private double conditionalProbability()
    {

      int index = 0;
      for ( int i = 0; i < parents.length; i++ ) {
        if ( parents[i].value == false ) {
          index += Math.pow( 2, parents.length - i - 1 );
        }
      }
      return probs[index];
    }

  /* Same as above except ignores the node at then center of a markove blanked */
  private double conditionalProbabilityMar(Node m)
    {

      double prob =1;

      for ( int i = 0; i < parents.length; i++ ) {
        if ( parents[i]==m) continue;
        prob *= parents[i].conditionalProbability();
      }
      return prob;
    }

  }

  // The list of nodes in the Bayes net
  private Node[] nodes;

  // A collection of examples describing whether Bot B is { cocky, bluffing
  // }
  public static final boolean[][] BBLUFF_EXAMPLES = { { true, true },
    { true, true }, { true, true }, { true, false }, { true, true },
    { false, false }, { false, false }, { false, true },
    { false, false }, { false, false }, { false, false },
    { false, false }, { false, true }
  };

  /**
   * Constructor that sets up the Poker-game network.
   */
  public BayesNet()
  {

    nodes = new Node[7];

    nodes[0] = new Node( "B.Cocky", new Node[] {}, new double[] { 0.05 } );
    nodes[1] = new Node( "B.Bluff", new Node[] { nodes[0] }, calculateBBluffProbabilities( BBLUFF_EXAMPLES ) );

    nodes[2] = new Node( "A.Deals", new Node[] {}, new double[] { 0.5 } );
    nodes[3] = new Node( "A.GoodHand", new Node[] { nodes[2] }, new double[] { 0.75, 0.5 } );
    nodes[4] = new Node( "B.GoodHand", new Node[] { nodes[2] }, new double[] { 0.4, 0.5 } );

    nodes[5] = new Node( "B.Bets", new Node[] { nodes[1], nodes[4] }, new double[] { 0.95, 0.7, 0.9, 0.01 } );
    nodes[6] = new Node( "A.Wins", new Node[] { nodes[3], nodes[4] }, new double[] { 0.45, 0.75, 0.25, 0.55 } );
  }

  /**
   * Prints the current state of the network to standard out.
   */
  public void printState()
  {

    for ( int i = 0; i < nodes.length; i++ ) {
      if ( i > 0 ) {
        System.out.print( ", " );
      }
      System.out.print( nodes[i].name + " = " + nodes[i].value );
    }
    System.out.println();
  }

  /**
   * Calculates the probability that Bot B will bluff based on whether it is
   * cocky or not.
   *
   * @param bluffInstances
   *            A set of training examples in the form { cocky, bluff } from
   *            which to compute the probabilities.
   * @return The probability that Bot B will bluff when it is { cocky, !cocky
   *         }.
   */
  public double[] calculateBBluffProbabilities( boolean[][] bluffInstances )
  {
    double[] probabilities = {0, 0};
    int[] counts = {0, 0};
    
    for ( boolean[] inst : bluffInstances ) {
      //basically using cocky to index probabilities
      //and bluff to add or not add to count
      int cocky =  (inst[0]) ? 0 : 1;
      int bluff =  (inst[1]) ? 1 : 0;

      probabilities[ cocky ] += bluff;
      counts[ cocky ] += 1;
    }
    //probabilities[0] is the bluff given cocky count
    //probabilities[1] is the bluff given not cocky count
    probabilities[0] /= counts[0]; //turn into prob
    probabilities[1] /= counts[1];
    
    return probabilities;
  }

  /**
   * This method calculates the exact probability of a given event occurring,
   * where all variables are assigned a given evidence value.
   *
   * @param evidenceValues
   *            The values of all nodes.
   * @return -1 if the evidence does not cover every node in the network.
   *         Otherwise a probability between 0 and 1.
   */
  public double calculateExactEventProbability( boolean[] evidenceValues )
  {
    // Only performs exact calculation for all evidence known.
    if ( evidenceValues.length != nodes.length ) {
      return -1;
    }

    for( int i = 0; i < nodes.length; i++ ) {
      nodes[i].value = evidenceValues[i];
    }
    double prob = 1;
    for( Node n : nodes ) {
      double condp = ( n.value ) ? n.conditionalProbability() : 1 - n.conditionalProbability();
      //System.out.println(n.name+"("+n.value+") = "+condp);
      prob *= condp;
    }

    return prob;
  }

  /**
   * This method assigns new values to the nodes in the network by sampling
   * from the joint distribution (based on PRIOR-SAMPLE method from text
   * book/slides).
   */
  public void priorSample()
  {
    Random randgen = new Random();

    for( int x = 0; x < nodes.length; x++ ) {
      nodes[x].value  = randgen.nextDouble() < nodes[x].conditionalProbability();
    }
  }

  /**
   * This Method checks to see if sample matches evidence
   */
  public boolean CheckEvidence(int[] indicesOfEvidenceNodes, boolean[] evidenceValues){
    for(int i=0; i<indicesOfEvidenceNodes.length; i++){
      if( nodes[ indicesOfEvidenceNodes[i] ].value != evidenceValues[i])
        return false;
    }
    return true;
  }

  /**
   * Rejection sampling. Returns probability of query variable being true
   * given the values of the evidence variables, estimated based on the given
   * total number of samples (see REJECTION-SAMPLING method from text
   * book/slides).
   *
   * The nodes/variables are specified by their indices in the nodes array.
   * The array evidenceValues has one value for each index in
   * indicesOfEvidenceNodes. See also examples in main().
   *
   * @param queryNode
   *            The variable for which rejection sampling is calculating.
   * @param indicesOfEvidenceNodes
   *            The indices of the evidence nodes.
   * @param evidenceValues
   *            The values of the indexed evidence nodes.
   * @param N
   *            The number of iterations to perform rejection sampling.
   * @return The probability that the query variable is true given the
   *         evidence.
         *
         * // Probability of B.GoodHand given bet and A not win.
  	b.rejectionSampling(4, new int[] { 5, 6 }, new boolean[] { true, false }, 10000));
                                *
   */
  public double rejectionSampling( int queryNode,
        int[] indicesOfEvidenceNodes, boolean[] evidenceValues, int N )
  {
    double[] counts = new double[2];

    for( int x = 0; x < N; x++ ) {
      priorSample();//generate sample
      /* Check consistent with evidence */
      if(!CheckEvidence(indicesOfEvidenceNodes, evidenceValues)) continue;
      counts[ (nodes[queryNode].value) ? 0:1 ]++;
    }
    return counts[0]/(counts[0]+counts[1]);
  }

  /**
   * This method assigns new values to the non-evidence nodes in the network
   * and computes a weight based on the evidence nodes (based on
   * WEIGHTED-SAMPLE method from text book/slides).
   *
   * The evidence is specified as in the case of rejectionSampling().
   *
   * @param indicesOfEvidenceNodes
   *            The indices of the evidence nodes.
   * @param evidenceValues
   *            The values of the indexed evidence nodes.
   * @return The weight of the event occurring.
   *
   */
  public double weightedSample( int[] indicesOfEvidenceNodes,
                                boolean[] evidenceValues )
  {
    Random randgen = new Random();
    double W = 1.0;
    int inode = 0;
        
    for(int i=0; i<nodes.length; i++){
      /* Is Evidence */
      if( inode<indicesOfEvidenceNodes.length &&
                indicesOfEvidenceNodes[inode] == i ){
        nodes[i].value = evidenceValues[inode++];
        W=W*nodes[i].conditionalProbability();
      }else{
        /* Sample */
        nodes[i].value = randgen.nextDouble() < nodes[i].conditionalProbability();
      }
    }
    
    return W; 
  }

  /**
   * Likelihood weighting. Returns probability of query variable being true
   * given the values of the evidence variables, estimated based on the given
   * total number of samples (see LIKELIHOOD-WEIGHTING method from text
   * book/slides).
   *
   * The parameters are the same as in the case of rejectionSampling().
   *
   * @param queryNode
   *            The variable for which rejection sampling is calculating.
   * @param indicesOfEvidenceNodes
   *            The indices of the evidence nodes.
   * @param evidenceValues
   *            The values of the indexed evidence nodes.
   * @param N
   *            The number of iterations to perform rejection sampling.
   * @return The probability that the query variable is true given the
   *         evidence.
   */
  public double likelihoodWeighting( int queryNode,
                                     int[] indicesOfEvidenceNodes, boolean[] evidenceValues, int N )
  {
    double[] counts = new double[2];
    double w;
    for( int x = 0; x < N; x++ ) {
      w=weightedSample( indicesOfEvidenceNodes, evidenceValues );
      counts[ (nodes[queryNode].value) ? 0:1 ] += w; 
    }
    
    return counts[0]/(counts[0]+counts[1]) ;
    
  }


    public double MarkovBlanket(int nidx){
        double p=1;
        //double child_prob = 1;
        
        p *= nodes[nidx].conditionalProbability();
                    
        for(Node n : nodes){
          //Look for children
          if( Arrays.asList(n.parents).contains( nodes[nidx] ) ){
              p *= n.conditionalProbability();
              for(Node np : n.parents)
                if(np!=nodes[nidx]) //Childrens perents that arnt root node
                  p*=n.conditionalProbability();
          }
        }
        return p;     
    }

  /**
   * MCMC inference. Returns probability of query variable being true given
   * the values of the evidence variables, estimated based on the given total
   * number of samples (see MCMC-ASK method from text book/slides).
   *
   * The parameters are the same as in the case of rejectionSampling().
   *
   * @param queryNode
   *            The variable for which rejection sampling is calculating.
   * @param indicesOfEvidenceNodes
   *            The indices of the evidence nodes.
   * @param evidenceValues
   *            The values of the indexed evidence nodes.
   * @param N
   *            The number of iterations to perform rejection sampling.
   * @return The probability that the query variable is true given the
   *         evidence.
   */
  public double MCMCask( int queryNode, int[] indicesOfEvidenceNodes,
                         boolean[] evidenceValues, int N )
  {
    Random randgen = new Random();
    double[] counts = new double[2];

    /* Set evidence */
    for(int x=0; x<indicesOfEvidenceNodes.length; x++){
      nodes[ indicesOfEvidenceNodes[x] ].value = evidenceValues[x];
    }

    /* set random values */
    for(int x=0; x<nodes.length; x++){
      if( Arrays.asList(indicesOfEvidenceNodes).contains( x ) ) continue;
      nodes[x].value=randgen.nextBoolean();
    }
    
    for( int n = 0; n < N; n++ ) {
      counts[ (nodes[queryNode].value) ? 0:1 ]++; 

      /* For non evidence nodes */
      for(int x=0; x<nodes.length; x++){
        if( Arrays.asList(indicesOfEvidenceNodes).contains( x ) ) continue;
          nodes[x].value =  randgen.nextDouble() < MarkovBlanket(x);
          //System.out.println(MarkovBlanket(x)+", "+nodes[x].conditionalProbability());
      }
    }

    /* Normalize */
    return counts[0]/(counts[0]+counts[1]) ;
  }

  /**
   * The main method, with some example method calls.
   */
  public static void main( String[] ops )
  {

    // Create network.
    BayesNet b = new BayesNet();

    double[] bluffProbabilities = b.calculateBBluffProbabilities( BBLUFF_EXAMPLES );
    System.out.println( "When Bot B is cocky, it bluffs "
                        + ( bluffProbabilities[0] * 100 ) + "% of the time." );
    System.out.println( "When Bot B is not cocky, it bluffs "
                        + ( bluffProbabilities[1] * 100 ) + "% of the time." );

    double bluffWinProb = b.calculateExactEventProbability( new boolean[] {
                            true, true, true, false, false, true, false
                          } );
    System.out
    .println( "The probability of Bot B winning on a cocky bluff "
              + "(with bet) and both bots have bad hands (A dealt) is: "
              + bluffWinProb );

    // Sample five states from joint distribution and print them
    for ( int i = 0; i < 5; i++ ) {
      b.priorSample();
      b.printState();
    }

    // Print out results of some example queries based on rejection
    // sampling.
    // Same should be possible with likelihood weighting and MCMC inference.

    // Probability of B.GoodHand given bet and A not win.
    System.out.println("rs "+ b.rejectionSampling( 4, new int[] { 5, 6 },
                        new boolean[] { true, false }, 1000000 ) );
    System.out.println("lh "+ b.likelihoodWeighting( 4, new int[] { 5, 6 },
                        new boolean[] { true, false }, 1000000 ) );
    System.out.println("mc "+ b.MCMCask( 4, new int[] { 5, 6 },
                        new boolean[] { true, false }, 1000000 ) );                    

    System.out.println();
    
    // Probability of betting given a cocky
    System.out.println("rs "+ b.rejectionSampling( 1, new int[] { 0 },
                        new boolean[] { true }, 100000 ) );
    System.out.println("lh "+ b.likelihoodWeighting( 1, new int[] { 0 },
                        new boolean[] { true }, 100000 ) );
    System.out.println("mc "+ b.MCMCask( 1, new int[] { 0 },
                        new boolean[] { true }, 100000 ) );

   System.out.println();

    // Probability of B.Goodhand given B.Bluff and A.Deal
    System.out.println("rs "+ b.rejectionSampling( 4, new int[] { 1, 2 },
                        new boolean[] { true, true }, 100000 ) );
    System.out.println("lh "+ b.likelihoodWeighting( 4, new int[] { 1, 2 },
                        new boolean[] { true, true }, 100000 ) );
    System.out.println("mc "+ b.MCMCask( 4, new int[] { 1, 2 },
                        new boolean[] { true, true }, 100000 ) );

  }
}
