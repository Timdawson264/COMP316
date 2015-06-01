import sys
from array import array
import itertools

class BayesNode:
  NetNodes = dict() #used to build graph

  def __lt__(a, b):
    return a.name.__lt__(b.name)
  
  def __init__(self, S:str):
    self.cpt = dict()
    self.prob = dict()
    self.state=False
    name = S.split(':', 1)[0]
    parents = S.split(':', 1)[1].split()

    self.name = name
    #add to global list of nodes
    BayesNode.NetNodes[name] = self

    #add parents
    self.parents=list()
    for n in parents:
      self.parents.append( BayesNode.NetNodes[n] )

    #build CPT
    for x in itertools.product([False, True], repeat=len(parents)):
      cond = set()
      for nidx,s in enumerate(x):
        cond.add( (nidx, s) )
      self.cpt[frozenset(cond)] = [True,False] #Zero Freq
    
    print("New Node:",name,parents)

  def getCondSet(self):
    cond = set() #cond is the set of trues and falses
    for i,n in enumerate(self.parents):
      cond.add((i, n.state ))
    cond = frozenset(cond) #make hashable
    return cond

  def probUpdate(self):
    for cond in self.cpt.keys(): #for each condition
       Pt = self.cpt[ cond ].count(True)/len(self.cpt[ cond ])
       self.prob[ cond ] = Pt

  def cptUpdate(self):
    cond = self.getCondSet() #gets the condition key
    self.cpt[ cond ].append(self.state)
    
    
  
    

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
    
  
      
      

