import java.util.Random;

// java Random3Sat numVars numClauses randomSeed
public class Random3Sat {

  public static void main(String[] args) {
    
    new Random3Sat().doIt(args);

  }

  public void doIt(String[] args) {

    int numVars = Integer.parseInt( args[0]);
    int numClauses = Integer.parseInt( args[1]);
    long randomSeed = Long.parseLong( args[2]);

    System.out.println("cnf numVars = " + numVars + " numClauses = " + numClauses
		       + " randomSeed = " + randomSeed);

    Random r = new Random( randomSeed);

    for (int clause = 0; clause < numClauses; clause++) {
      randomClause(r,numVars);
    }
  }

  
  public void randomClause( Random r, int numVars) {
    int var1 = r.nextInt(numVars);
    int var2 = r.nextInt(numVars-1);
    if (var2 >= var1) {
      var2++;
    } else {
      int tmp = var1;
      var1 = var2;
      var2 = tmp;
    }
    int var3 = r.nextInt(numVars-2);
    if (var3 >= var1) {
      var3++;
    }
    if (var3 >= var2) {
      var3++;
    }
    var1++;
    var2++;
    var3++;
    String sign1 = r.nextBoolean() ? "-" : "";
    String sign2 = r.nextBoolean() ? "-" : "";
    String sign3 = r.nextBoolean() ? "-" : "";
    System.out.println( sign1+var1 + " " + sign2+var2 + " " + sign3+var3);
  }
}

