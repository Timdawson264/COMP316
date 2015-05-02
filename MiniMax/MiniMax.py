import numpy
import fileinput
import sys
import string
import math
import time
from enum import Enum

#   - abcdefgh
#   1 ........
#   2 ........
#   3 ........
#   4 ...OB...
#   5 ...BO...
#   6 ........
#   7 ........
#   8 ........
#   B 60

size = 8
size2 = size*size
ExpandedNodesCount = 0

class Token(Enum):
    Empty = 0
    Black = 1
    White = 2

    def otherplayer(self):
        if(self == Token.Black): return Token.White
        if(self == Token.White): return Token.Black
        
    def fromchar(t):
        if(t == '.'): return Token.Empty
        if(t == 'B'): return Token.Black
        if(t == 'O'): return Token.White
    def tochar(t):
        if(t == Token.Empty): return '.'
        if(t == Token.Black): return  'B'
        if(t == Token.White): return  'O'

    def __str__(self):
        return self.tochar()
        
class State(object):
    pos_moves = [ (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1), (1,1) ]
    
    def __init__(self, token_lst=[]): #init from list of token values
        if len(token_lst) == 0:
            self.board = numpy.zeros(size2, dtype=numpy.int8)
        else:
            self.board = numpy.array(token_lst, copy=True, dtype=numpy.int8)
        self.move = None
        
    def toString(self):
        S = ""
        S+= "- " + string.ascii_lowercase[:size] + "\n" # append header
        for y in range(0,size):
            S+= str(y+1) + " "
            for x in range(0,size):
                S += Token.tochar( Token(self.board[x+(y*size)]) )
            S+="\n"
        return S

    def Score(state,MaxPlayer, IsFinal=False, IsMax=False):
        #check if anymoves possible
        # END GAME CHECK
        score = int(0)

        if(IsFinal):
            if IsMax: score+=100
            else: score-=100
            
        for pos in range(0,state.board.size):
            if(state.board[pos] == MaxPlayer.value):
                score+=1
            if(state.board[pos] == MaxPlayer.otherplayer().value ):
                score-=1
        
        
        return score
        

    #finds all possible moves for player
    
    def PossibleMoves(state, player):
        mvs = set() #Valid move positions
        
        #Check around targets for ajacent emptys
        for pos in range(0,state.board.size):
            #not my own tokens and empty squares
            if( state.board[pos] == Token.Empty.value): continue
            if( state.board[pos] == player.value): continue

            captured = 0            
            y = math.floor(pos / size)
            x = pos % size
            for deltaxy in State.pos_moves:
                captureddir = 0
                dx = deltaxy[0]
                dy = deltaxy[1]
                cx = x-dx
                cy = y-dy
                #edge check
                if((dx+x) >= 0 and (dx+x) < size and (dy+y) >= 0 and (dy+y)<size):
                    if state.board[ ((dy+y)*size)+(dx+x) ] == Token.Empty.value: #Found Empty
                        while (cx >= 0 and cx < size and cy >= 0 and cy<size): 
                            if state.board[ (cy*size)+cx ] == player.otherplayer().value:
                                #Search down line for own pieace
                                cx -= dx
                                cy -= dy
                            else:
                                break
                        if(cx >= 0 and cx < size and cy >= 0 and cy<size):    
                            if state.board[ (cy*size)+cx ] == player.value:
                                mvs.add( (dx+x,dy+y) ) #we found our pieace
        return mvs
    
    def DoMoveR(state, Player, xy, dxy):
        cx = xy[0] + dxy[0]
        cy = xy[1] + dxy[1]

        #Out of bounds
        if not (cx >= 0 and cy >=0 and cx < size and cy < size):
            return False
        
        #Is a good move
        if state.board[ (cy*size)+cx ] == Player.value:
            return True
            
        if state.board[ (cy*size)+cx ] == Player.otherplayer().value:
            if state.DoMoveR(Player, (cx,cy), dxy): #if good direction capture all on way back
                state.board[ cx + (cy*size) ] = Player.value
                return True
        
        return False
    
    def DoMove(state, Player, xy):
        x = xy[0]
        y = xy[1]
        for deltaXY in State.pos_moves: #capture all possible tokens
            if state.DoMoveR(Player, xy, deltaXY):
                state.board[ x + (y*size) ] = Player.value 
                state.move = xy
    
    def Expand(self, Player):
        global ExpandedNodesCount
        ExpandedNodesCount+=1
        
        states = list()
        moves = self.PossibleMoves(Player)
        for move in moves:
            #generate states using the potential token posion
            newstate = State(token_lst=self.board)
            newstate.DoMove(Player, move)
            states.append(newstate)

        
        return states

def minimax(state, depth, MaxPlayer, IsMax, StopTime):
    #print(depth, state.toString())
    if depth == 0 or time.time() > StopTime:
        return state.Score(MaxPlayer)
        
    if IsMax:
        nstates = state.Expand(MaxPlayer)
    else:
        nstates = state.Expand(MaxPlayer.otherplayer())
        
    if len(nstates) == 0: #or node is a terminal node
        return state.Score(MaxPlayer)
        
    if IsMax:
        MaxValue = -sys.maxsize
        for child in nstates:
            val = minimax(child, depth - 1, MaxPlayer, False, StopTime)
            MaxValue = max(MaxValue, val)
                
        return MaxValue
    else:
        MinValue = sys.maxsize
        for child in nstates:
            val = minimax(child, depth - 1, MaxPlayer, True, StopTime)
            MinValue = min(MinValue, val)
        return MinValue
        
        
def minimaxAB(state, depth, MaxPlayer, IsMax, Alpha, Beta, StopTime):
    #print(depth, state.toString())
    if depth == 0 or time.time() > StopTime:
        return state.Score(MaxPlayer)
        
    if IsMax:
        nstates = state.Expand(MaxPlayer)
    else:
        nstates = state.Expand(MaxPlayer.otherplayer())
        
    if len(nstates) == 0: #or node is a terminal node
        return state.Score(MaxPlayer, IsFinal=True, IsMax=IsMax)
        
    if IsMax:
        MaxValue = -sys.maxsize
        for child in nstates:
            MaxValue = max( MaxValue, minimaxAB(child, depth - 1, MaxPlayer, False, Alpha, Beta, StopTime) )
            Alpha = max(Alpha, MaxValue)
            if Beta <= Alpha: break #Trim
        return MaxValue
    else:
        MinValue = sys.maxsize
        for child in nstates:
            MinValue = min( MinValue, minimaxAB(child, depth - 1, MaxPlayer, True, Alpha, Beta, StopTime) )
            Beta = min( Beta, MinValue)
            if Beta <= Alpha: break #trim
            
        return MinValue

def main():
    board = list()
    
    #TODO: some checking
    
    #Read Board in
    lines = sys.stdin.read(-1).splitlines(False)
    lines.pop(0) #pop header
    param = lines.pop() # pop footer
    
    #Strip off leading digits and whitespace and turn into tokens
    for line in lines: 
        for t in line.strip(string.digits+string.whitespace):
            board.append(Token.fromchar(t).value)
            
    inState = State(token_lst=board)
    param = param.split(" ")
    Player = Token.fromchar(param[0])
    TimeLimit = float(param[1])
    #print( "Player: " + Player.name, param[0] )
    #print( str(TimeLimit) + " second limit" ) 
    #print( "Input:\n" + inState.toString() )
    
    StopTime = time.time() + TimeLimit

    MaxDepth = 0
    BestMove = State()
    MaxValue = -sys.maxsize
    global ExpandedNodesCount
    while time.time() < StopTime:
        #Expand First Node and Mini Max each one then Save the Best Node

        nstates = inState.Expand(Player)
        if len(nstates)==0 :
            print("move a -1 nodes 0 depth 0 minimax 0") #No Moves
        
        for child in nstates: 
            val = minimaxAB(child, MaxDepth, Player, False, -sys.maxsize, sys.maxsize, StopTime)
            #val = minimax(child, MaxDepth, Player, False, StopTime)
            if val > MaxValue:
                BestMove = child #This is a better move
            MaxValue = max(MaxValue, val)
        MaxDepth+=1

    
    print("move", string.ascii_lowercase[BestMove.move[0]], BestMove.move[1]+1, "nodes", ExpandedNodesCount ,"depth", MaxDepth, "minimax", MaxValue) 
    #sys.stdout.write(BestMove.toString() + Player.otherplayer().tochar() +" "+ str(int(TimeLimit))+ "\n" )
    #while CurrentLevel < Maxlevel:
    #nextStates = curState.Expand(Player)
    
    
if __name__ == "__main__":
    main()
