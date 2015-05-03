#!/usr/bin/python

import sys
import string
import math
import time
import re
import numpy
import random

TIMELIMIT = 60*5 #5 Minut Limit
StartTime = None

def ClausesSatisfied(Clauses, Model):
  for Clause in Clauses:
    l1=Clause[0]
    l2=Clause[1]
    l3=Clause[2]
    #if more then one literal is true in the disjunction
    if( (Model.count(l1)+Model.count(l2)+Model.count(l3) ) == 0 ):
      return False
  return True

def ClausesContainsUnsatasfiable(Clauses, Symbols, Model):
  for Clause in Clauses:
      l1=Clause[0]
      l2=Clause[1]
      l3=Clause[2]
      #Literals of Clause not in Model and Not in unassigned symbols
      if( Symbols.count( abs(l1) )==0 and Model.count(l1)+Model.count(-l1)==0 ):
        if( Symbols.count( abs(l2) )==0 and Model.count(l2)+Model.count(-l2)==0 ):
          if( Symbols.count( abs(l3) )==0 and Model.count(l3)+Model.count(-l3)==0 ):
            return True #Clause cant be satisfied by model or remaining symbols
  return False

def ListOfPures(Clauses):
  pos = numpy.unique(Clauses[Clauses>0])
  neg = numpy.unique(Clauses[Clauses<0])
  pures = numpy.setxor1d(pos,abs(neg))
  pos = numpy.intersect1d(pures, pos)
  neg = numpy.intersect1d(pures*-1, neg)

  return numpy.append(pos,neg)

def isUnitClause(Clause, Symbols, Model):
  l1=Clause[0]
  l2=Clause[1]
  l3=Clause[2]

  #Unsatisfied Clause and only one literal left to assign
  if( (Model.count(l1)+Model.count(l2)+Model.count(l3) ) == 0 ):
    if( Symbols.count(abs(l1))+Symbols.count(abs(l2))+Symbols.count(abs(l3)) == 1):
      return True
  
  return False

def unitPropagate(Clause, Symbols, Model):
  for l in Clause:
    if(Symbols.count(abs(l))>0): #is symbol that needs assigning
      Symbols.remove(abs(l))
      Model.append(l)
  
#Clauses is a list of clauses, Symbols is a list of un assigned Literals, Model are assigned Literals
def DPLL(Clauses, Symbols, Model):
  #Check Time Limit
  if((time.time()-StartTime)>TIMELIMIT):
    return False
  
  #print("DPLL:", Clauses, Symbols, Model)
  #if every clause in clauses is true in model then return true
  if ClausesSatisfied(Clauses, Model):
    return True
  
  #if some clause in clauses is False in model then return false
  if ClausesContainsUnsatasfiable(Clauses, Symbols, Model):
    print("NO SAT")
    return False


  #Assign Pure Symbols
  for l in ListOfPures(Clauses):
    if( Symbols.count( abs(l) ) > 0 ):
      Symbols.remove(abs(l)) #remove from unassined
      Model.append(l) #Assigen to make pure go away
      return DPLL(Clauses, Symbols.copy(), Model.copy())
  
  #Find And Assign Unit Clauses
  for Clause in Clauses:
    if(isUnitClause(Clause, Symbols, Model)):
      unitPropagate(Clause, Symbols, Model)
      return DPLL(Clauses, Symbols.copy(), Model.copy())

  if len(Symbols)==0:
    return False
  l = Symbols.pop(0)
  NewModelA = Model.copy()
  NewModelB = Model.copy()
  NewModelA.append(l)
  NewModelB.append(-l)
  
  if DPLL(Clauses, Symbols.copy(), NewModelA): return True
  if DPLL(Clauses, Symbols.copy(), NewModelB): return True
  return False
  
def main():
  global StartTime
  StartTime = time.time()

  clausesStr = open(sys.argv[1], 'r').read(None).splitlines(False) #Read File
  header = clausesStr.pop(0)
  header = re.compile('cnf numVars = (\d*) numClauses = (\d*) randomSeed = (\d*)').findall(header)[0]
  
  numVars = int(header[0])
  numClauses = int(header[1])
  randomSeed = int(header[2])


  #This array contains all clauses.
  Clauses = numpy.zeros((numClauses,3), numpy.int64) #Array of Clauses each etery contains the 3 sat literals
  Symbols = list(range(1,numVars+1))
  Model = list()

  #Read in Clauses from file
  for clause in enumerate(clausesStr):
    clausenum = clause[0]
    clause=clause[1].split(" ")
    Clauses[clausenum][0] = int(clause[0])
    Clauses[clausenum][1] = int(clause[1])
    Clauses[clausenum][2] = int(clause[2])

  #print( ListOfPures(Clauses) )
  res = DPLL(Clauses, Symbols, Model)
  print(sys.argv[1],res,"time:",time.time()-StartTime) #print solution
    
if __name__ == "__main__":
  main()
