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
    
  def getCondProb(self):
    cond = self.getCondSet() #gets the condition key
    p = self.prob[cond] #prob of node true
    if self.state==False: p = 1-p
    return p
