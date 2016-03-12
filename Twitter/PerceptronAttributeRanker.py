import sys
import math
import numpy as np

from Perceptron import Perceptron


if __name__ == "__main__":
  
  SentimentData = open(sys.argv[1], 'r').read(-1).splitlines(False) #Read File
  Header = SentimentData.pop(0).split(",")
  SentimentData = [ s.split(",") for s in SentimentData ] #pre split
  
  while len(Header)>1:
    
    Percpt = Perceptron(len(Header)-1, float(sys.argv[2]) ) #Create Perceptron
    AvgAbsWeights = np.zeros(len(Header), dtype=np.float)
    for case in SentimentData:
      #copy inputs into Perceptron
      case = [ bool(int(c)) for c in case ]
      Percpt.Train(case)
      AvgAbsWeights += np.absolute(Percpt.weights)
    AvgAbsWeights /= len(SentimentData)
    AvgAbsWeights[0] = 0 #Disable Bias Weight
    
    midx = np.argmax(AvgAbsWeights)-1 #get max idx
    print(Header[midx], len(SentimentData)-Percpt.err )

    #remove the max from dataset
    Header.pop(midx)
    for s in SentimentData:
      s.pop(midx)
        
