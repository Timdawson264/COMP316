#!/usr/bin/python

import sys
import string
import math
import time
import re
import numpy
import random

RANDPROB = 0.2
MAXFLIPS = 10**7

@profile
def ClauseisSatisfied(Clause, Literals):
  #resolve each bool
  #First find value then negate if needed
  l1 = Literals[abs(Clause[0])-1]^(Clause[0]<0)
  l2 = Literals[abs(Clause[1])-1]^(Clause[1]<0)
  l3 = Literals[abs(Clause[2])-1]^(Clause[2]<0)
  return (l1)|(l2)|(l3)

@profile
def isSatisfied(Clauses, Literals):
  for c in Clauses:
    if ClauseisSatisfied(c, Literals) == False:
      return False
  return True

#Returns a list of unsatified clauses
@profile
def unSatisfied(Clauses, Literals):
  uc = list()
  for c in enumerate(Clauses):
    if ClauseisSatisfied(c[1], Literals) == False:
      uc.append(c[0])
  return uc

def numUnSatisfied(Clauses, Literals):
  uc = 0
  for c in (Clauses):
    if ClauseisSatisfied(c, Literals) == False:
      uc+=1
  return uc

@profile
def BestLiteral(Clause, Clauses, Literals):
  Best = None
  BestSize =  len(Clauses)
  
  for l in Clauses[Clause]:
    #tmp flip
    Literals[ (abs(l)-1) ]^=1 #Xor 1 
    if( numUnSatisfied(Clauses, Literals) < BestSize):
      Best=l 
    Literals[ (abs(l)-1) ]^=1 #Xor 1 
  return Best

#rewite BestLiteral so it does a search instead of calling numUnSat
def BestLiteralNew(Clause, Clauses, Literals):
  Best = None
  BestSize =  len(Clauses)

  for l in Clauses[Clause]:
    exit()
    
@profile
def main():
  print("Using:",sys.argv[1])
  clausesStr = open(sys.argv[1], 'r').read(None).splitlines(False) #Read File
  header = clausesStr.pop(0)
  header = re.compile('cnf numVars = (\d*) numClauses = (\d*) randomSeed = (\d*)').findall(header)[0]
  
  numVars = int(header[0])
  numClauses = int(header[1])
  randomSeed = int(header[2])
  print(numVars, numClauses, randomSeed)

  #This array contains all clauses.
  clausesA = numpy.zeros((numClauses,3), numpy.int64)
  literalVals = numpy.zeros(numVars, numpy.bool8)
    
  for clause in enumerate(clausesStr):
    clausenum = clause[0]
    clause=clause[1].split(" ")
    clausesA[clausenum][0] = int(clause[0])
    clausesA[clausenum][1] = int(clause[1])
    clausesA[clausenum][2] = int(clause[2])

  #Randomly set all the literals
  for x in range(numVars):
    literalVals[x] = random.getrandbits(1)

  for flip in range(MAXFLIPS):
      
    if(isSatisfied(clausesA,literalVals)):
      print("Solved in:",flip, literalVals) #print solution
      return
    #else:
      #print( len(unSatisfied(clausesA,literalVals)), "{:.2%}".format((flip/MAXFLIPS)*100)  )

    #list of unsatified clauses, Pick one at random
    unsat = unSatisfied(clausesA,literalVals)
    unsat = unsat[ random.randrange( len(unsat) ) ]
    
    if(random.random()<RANDPROB):
      #random flip literal
      literalVals[ (abs(random.choice(clausesA[unsat]))-1) ]^=1 #Xor 1 
    else:
      #Choice Best literal from clause to flip
      best = BestLiteralNew(unsat, clausesA, literalVals)
      if(best!=None):
        literalVals[ (abs(best)-1) ]^=1 #Xor 1
      else: #If no best flip random
        literalVals[ (abs(random.choice(clausesA[unsat]))-1) ]^=1 #Xor 1
        
if __name__ == "__main__":
  main()
