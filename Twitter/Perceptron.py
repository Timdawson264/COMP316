import sys
import math
import numpy as np

class Perceptron:
  #sigmoid
  #g(x)  = 1/( 1 + e^-x )
  #g'(x) = g(x) * (1 - g(x))

  def sig(x):
    return 1/( 1 + math.exp(-x) )

  def sigdif(x):
    return Perceptron.sig(x) * ( 1 - Perceptron.sig(x) )

  def __init__(self, size, alpha):
    self.inputs = np.zeros(size+1, dtype=np.int8 )
    self.weights = np.zeros(size+1, dtype=np.float )
    self.alpha = alpha
    self.err = 0
  
  def CalcOut(self):
    out = np.sum( self.inputs*self.weights )
    out = Perceptron.sig(out)
    return out
    
  #square error
  def SqErr(self,Expected):
   return  0.5 * pow( ( int(Expected) - self.CalcOut()), 2)
    
  def Err(self, Expected):
    return Expected - self.CalcOut()

  def updateWeights(self,Expected):
    sigd = Perceptron.sigdif( np.sum( self.inputs*self.weights ) )
    update = self.alpha * self.Err(Expected) * sigd
    #do update
    self.weights = self.weights + (self.inputs * update)
  
  def Train(self, data):
    #data is array of inputs where last item is expected result
    ExptResult = data.pop()
    data.insert(0,-1) #dont forget bias in inputs
    self.inputs = np.copy(data) #inputs are now set

    self.err += int( (self.CalcOut()>0.5)!=ExptResult)

    self.updateWeights(ExptResult) 
    
if __name__ == "__main__":
  

  SentimentData = open(sys.argv[1], 'r').read(-1).splitlines(False) #Read File
  Header = SentimentData.pop(0).split(",")

  Percpt = Perceptron(len(Header)-1, float(sys.argv[2]) ) #Create Perceptron
  
  for case in SentimentData:
    #copy inputs into Perceptron
    case = case.split(",")
    case = [ bool(int(c)) for c in case ]
    Percpt.Train(case)

  
  weights = [ str(w) for w in Percpt.weights ]
  print(",".join(weights))
  
  print(Percpt.err,"Classification errors")
  print(1-(Percpt.err/len(SentimentData)), "Correct")
