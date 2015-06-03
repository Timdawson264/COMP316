import sys
from array import array
import itertools

from BayesNet import *
  
    

if __name__ == "__main__":
  netFile = open(sys.argv[1])
  trainFile = open(sys.argv[2])
  outputFile = open("output.txt",mode="w")

  print("Reading Network From:",sys.argv[1])
  print("Reading Training Data From:",sys.argv[2])

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

  #Traning done calculate probabilities
  for name,node in BayesNode.NetNodes.items():
    node.probUpdate()
    
  #output CPT
  for name,node in BayesNode.NetNodes.items():
    if(len(node.cpt)==1): continue #Skip if not conditions

    #Create nice truth table for this node
    tt = itertools.product(['0', '1'], repeat=len(node.parents))
    tt = [", ".join(x) for x in tt]

    cpt = [(sorted(k),v)  for k,v in node.cpt.items()]
    cpt.sort()
    cpt = list(list(zip(*cpt))[1])

    prob = [(sorted(k),v)  for k,v in node.prob.items()]
    prob.sort()
    prob = list(list(zip(*prob))[1])

    outputFile.write("\n")
    outputFile.write(name+":\n")#this node name
    outputFile.write( " ".join([n.name for n in node.parents])+"\n" ) # parent names
    
    for t,p in zip(tt,prob):  
      p = format(p, '.3f')
      outputFile.write(t+", "+p+"\n")
      #print(t,"\t\t",p)
      
      

