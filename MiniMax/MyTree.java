import java.util.Random;

// call as:
// java MyTree <YourID>

public class MyTree {

  public static void main(String[] args) {

    long seed = Long.parseLong( args[0]);
    System.out.println("id = " + seed + "\n");
    Random r = new Random(seed);

    new MyTree().printMyTree( r);
  }

  public void printMyTree( Random r) {
          System.out.println(
"                                       +--------- " + h(r) + "\n" +
"                                       |\n" +
"                             +---------min " + randomDirection(r) + "\n" +
"                             |         |\n" +
"                             |         +--------- " + h(r) + "\n" +
"                             |\n" +
"                   +---------MAX " + randomDirection(r) + "\n" +
"                   |         |\n" +
"                   |         |         +--------- " + h(r) + "\n" +
"                   |         |         |\n" +
"                   |         +---------min " + randomDirection(r) + "\n" +
"                   |                   |\n" +
"                   |                   +--------- " + h(r) + "\n" +
"                   |\n" +
"         +---------min " + randomDirection(r) + "\n" +
"         |         |\n" +
"         |         |                   +--------- " + h(r) + "\n" +
"         |         |                   |\n" +
"         |         |         +---------min " + randomDirection(r) + "\n" +
"         |         |         |         |\n" +
"         |         |         |         +--------- " + h(r) + "\n" +
"         |         |         |\n" +
"         |         +---------MAX " + randomDirection(r) + "\n" +
"         |                   |\n" +
"         |                   |         +--------- " + h(r) + "\n" +
"         |                   |         |\n" +
"         |                   +---------min " + randomDirection(r) + "\n" +
"         |                             |\n" +
"         |                             +--------- " + h(r) + "\n" +
"         |\n" +
"---------MAX " + randomDirection(r) + "\n" +
"         |\n" +
"         |                             +--------- " + h(r) + "\n" +
"         |                             |\n" +
"         |                   +---------min " + randomDirection(r) + "\n" +
"         |                   |         |\n" +
"         |                   |         +--------- " + h(r) + "\n" +
"         |                   |\n" +
"         |         +---------MAX " + randomDirection(r) + "\n" +
"         |         |         |\n" +
"         |         |         |         +--------- " + h(r) + "\n" +
"         |         |         |         |\n" +
"         |         |         +---------min " + randomDirection(r) + "\n" +
"         |         |                   |\n" +
          "         |         |                   +--------- " + h(r) + "\n" +
"         |         |\n" +
"         +---------min " + randomDirection(r) + "\n" +
"                   |\n" +
          "                   |                   +--------- " + h(r) + "\n" +
"                   |                   |\n" +
"                   |         +---------min " + randomDirection(r) + "\n" +
"                   |         |         |\n" +
"                   |         |         +--------- " + h(r) + "\n" +
"                   |         |\n" +
"                   +---------MAX " + randomDirection(r) + "\n" +
"                             |\n" +
"                             |         +--------- " + h(r) + "\n" +
"                             |         |\n" +
"                             +---------min " + randomDirection(r) + "\n" +
"                                       |\n" +
"                                       +--------- " + h(r) + "\n" 
		                   );
  }


  public String randomDirection( Random r) {
          return (r.nextBoolean()) ? "UP" : "DOWN";
  }

  public int h( Random r) {
          return r.nextInt(11) - 5;
  }
}

/*
Sample output for ID = 1234567

java MyTree 1234567
id = 1234567

                                       +--------- 3
                                       |
                             +---------min UP
                             |         |
                             |         +--------- -1
                             |
                   +---------MAX DOWN
                   |         |
                   |         |         +--------- -3
                   |         |         |
                   |         +---------min DOWN
                   |                   |
                   |                   +--------- 5
                   |
         +---------min UP
         |         |
         |         |                   +--------- -5
         |         |                   |
         |         |         +---------min DOWN
         |         |         |         |
         |         |         |         +--------- 5
         |         |         |
         |         +---------MAX UP
         |                   |
         |                   |         +--------- 2
         |                   |         |
         |                   +---------min DOWN
         |                             |
         |                             +--------- -2
         |
---------MAX DOWN
         |
         |                             +--------- -2
         |                             |
         |                   +---------min DOWN
         |                   |         |
         |                   |         +--------- -4
         |                   |
         |         +---------MAX UP
         |         |         |
         |         |         |         +--------- -1
         |         |         |         |
         |         |         +---------min DOWN
         |         |                   |
         |         |                   +--------- 0
         |         |
         +---------min UP
                   |
                   |                   +--------- 0
                   |                   |
                   |         +---------min UP
                   |         |         |
                   |         |         +--------- -3
                   |         |
                   +---------MAX DOWN
                             |
                             |         +--------- 2
                             |         |
                             +---------min UP
                                       |
                                       +--------- -5

*/






