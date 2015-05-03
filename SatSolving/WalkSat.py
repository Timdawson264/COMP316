#!/usr/bin/python

import sys
import string
import math
import time
import re
import numpy
import random

RANDPROB = 0.5
MAXFLIPS = 10**6

def ClauseisSatisfied(Clause, Literals):
  #resolve each bool
  #First find value then negate if needed
  #l1 = Literals[abs(Clause[0])-1]^(Clause[0]<0)
  #l2 = Literals[abs(Clause[1])-1]^(Clause[1]<0)
  #l3 = Literals[abs(Clause[2])-1]^(Clause[2]<0)
  #l = (l1)|(l2)|(l3)
  #return (l1)|(l2)|(l3)

  #VECTORIZED
  #the literals of the clause as bools
  lits = (Literals[abs(Clause)-1])
  lits ^= (Clause<0) #XOR the Nots, ie the negative numbers
  lv = lits[0]|lits[1]|lits[2]
  
  return lv
    

#Updates entire Clause satifsfaction array
def ClauseSatUpdate(Clauses, Literals, ClauseSat):
  for c in enumerate(Clauses):
    ClauseSat[c[0]] = ClauseisSatisfied(c[1], Literals)

#This updates only the clause that have changed because of a single literal flip
def ClauseSatUpdateLiteralFlip(literal, Clauses, Literals, ClauseSat):
  Literals[ (literal-1) ]^=1 #Flip the literal
  ClausesIdxs = numpy.where(abs(Clauses)==literal)[0] #find clauses containing said literal
  for ci in ClausesIdxs: #ci is a clause index
    ClauseSat[ci] = ClauseisSatisfied(Clauses[ci], Literals) #update each clause
    
#This function basically flips a single literal then checks what the net outcome is and returns that
def ClauseSatUpdateLiteralTest(literal, Clauses, Literals, ClauseSat):
  cs = numpy.where(numpy.absolute(Clauses)==literal)[0] #find clause containing literal
  delta = 0
  for ci in cs: #see what happens when we flip
    before = ClauseSat[ci] #original state of clause
    Literals[ (literal-1) ]^=1
    after = ClauseisSatisfied(Clauses[ci], Literals) #state after flip
    Literals[ (literal-1) ]^=1
    delta +=  int(after) - int(before) #Outcome of flip is either -1,0,1 
    
  return  delta 


def numSatisfied(ClauseSat):
  return numpy.count_nonzero(ClauseSat)

def BestLiteral(ClauseI, Clauses, Literals, ClauseSat):
  Best = Clauses[ClauseI][ random.randrange( 3 ) ] #start with random literal
  
  BestSize = numpy.count_nonzero(ClauseSat) #current satasfied clause count
  for l in Clauses[ClauseI]:
    #Flip and see what the outcome is interms of howmany now fail/succeed
    delta = ClauseSatUpdateLiteralTest(abs(l), Clauses, Literals, ClauseSat)
    if( delta+BestSize >= BestSize):
      Best=l
      
  return Best

    

def main():
  StartTime = time.time()
  
  clausesStr = open(sys.argv[1], 'r').read(None).splitlines(False) #Read File
  header = clausesStr.pop(0)
  header = re.compile('cnf numVars = (\d*) numClauses = (\d*) randomSeed = (\d*)').findall(header)[0]
  
  numVars = int(header[0])
  numClauses = int(header[1])
  randomSeed = int(header[2])

  #This array contains all clauses.
  clausesA = numpy.zeros((numClauses,3), numpy.int64) #Array of Clauses each etery contains the 3 sat literals
  clauseSat = numpy.zeros(numClauses, numpy.bool8) #Array of bools that are the precomputed resulte of every clause
  literalVals = numpy.zeros(numVars, numpy.bool8) #a bool array of every literals current state used to compute clauseSat

  #Read in Clauses from file
  for clause in enumerate(clausesStr):
    clausenum = clause[0]
    clause=clause[1].split(" ")
    clausesA[clausenum][0] = int(clause[0])
    clausesA[clausenum][1] = int(clause[1])
    clausesA[clausenum][2] = int(clause[2])

  #Randomly set all the literals
  for x in range(numVars):
    literalVals[x] = random.getrandbits(1)
  #compute the inital Clause state
  ClauseSatUpdate(clausesA, literalVals, clauseSat)
  
  for flip in range(MAXFLIPS):
      
    if(numSatisfied(clauseSat)==numClauses):
      print(sys.argv[1],"flips:",flip,"time:",time.time()-StartTime) #print solution
      return

    unsat = numpy.where(numpy.invert(clauseSat))[0] #array of indexes of unsatisfied clauses
    unsat = unsat[ random.randrange( len(unsat) ) ] #pick one at random
    #unsat - contains the index of a cluase that is not satisfied
    
    if(random.random()<RANDPROB):
      #random flip literal from clause
      c = clausesA[unsat] #get the literals for this clause
      l = abs(random.choice(c)) #pick a random literal from clause
      ClauseSatUpdateLiteralFlip(l, clausesA, literalVals, clauseSat) #Flip this literal
    else:
      best = BestLiteral(unsat, clausesA, literalVals, clauseSat) #Find the best Literal to flip
      ClauseSatUpdateLiteralFlip( abs(best) , clausesA, literalVals, clauseSat) #flip this literal

  print(sys.argv[1],"DNF","time:",time.time()-StartTime) #print solution
if __name__ == "__main__":
  main()
