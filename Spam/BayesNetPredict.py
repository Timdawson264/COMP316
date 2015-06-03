import sys
from array import array

from BayesNet import *


if __name__ == "__main__":
  netFile = open(sys.argv[1])
  trainFile = open(sys.argv[2])
  testFile = open(sys.argv[3])
  outputFile = open("completedTest.csv",mode="w")

  print("Reading Network From:",sys.argv[1])
  print("Reading Training Data From:",sys.argv[2])
  print("Reading Test Data From:",sys.argv[3])

  #build network of nodes
  netstr = netFile.read(-1).splitlines(False)
  for n in netstr:
    BayesNode(n)
  del netstr

  #calculate cond probs table
  trainstr = trainFile.read(-1).splitlines(False)
  header = trainstr.pop(0).split(",")

  for case in trainstr:
    #set all states
    case=case.split(",")
    for idx,state in enumerate(case):
      if header[idx] in BayesNode.NetNodes:
        #set state from train data
        BayesNode.NetNodes[header[idx]].state = bool(int(state))
    #All states set now update conditional prob for all nodes in net
    for name,node in BayesNode.NetNodes.items():
      node.cptUpdate()

  #Traning done calculate probabily tables
  for name,node in BayesNode.NetNodes.items():
    node.probUpdate()
    
  #calculate cond probs table
  testStr = testFile.read(-1).splitlines(False)
  header = testStr.pop(0).split(",")
  outputFile.write(",".join(header)+"\n")
  
  for case in testStr:
    #set all states
    case=case.split(",")
    for idx,state in enumerate(case):
      if header[idx] in BayesNode.NetNodes:
        #set state from train data
        if header[idx]=="spam":
          #time todo math
          #set spam true
          BayesNode.NetNodes[header[idx]].state = True
          isSpam = 1
          notSpam = 1
          for name,node in BayesNode.NetNodes.items():
            isSpam*=node.getCondProb()
          #set spam false
          BayesNode.NetNodes[header[idx]].state = False
          for name,node in BayesNode.NetNodes.items():
            notSpam*=node.getCondProb()

          if isSpam>notSpam:
            case[idx]="1"
          else:
            case[idx]="0"
                      
          outputFile.write(",".join(case)+"\n")
          
        else:
          BayesNode.NetNodes[header[idx]].state = bool(int(state))

