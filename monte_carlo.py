from math import *
import random

class OthelloState:
    def __init__(self,size = 8):
        self.playerJustMoved = 2 
        self.board = [] 
        self.size = size
        assert size == int(size) and size % 2 == 0 
        for y in range(size):
            self.board.append([0]*size)
        self.board[size/2][size/2] = self.board[size/2-1][size/2-1] = 1
        self.board[size/2][size/2-1] = self.board[size/2-1][size/2] = 2

    def Clone(self):
        st = OthelloState()
        st.playerJustMoved = self.playerJustMoved
        st.board = [self.board[i][:] for i in range(self.size)]
        st.size = self.size
        return st

    def make_move(self, move):
        (x,y)=(move[0],move[1])
        assert x == int(x) and y == int(y) and self.is_valid(x,y) and self.board[x][y] == 0
        m = self.GetAllSandwichedCounters(x,y)
        self.playerJustMoved = 3 - self.playerJustMoved
        self.board[x][y] = self.playerJustMoved
        for (a,b) in m:
            self.board[a][b] = self.playerJustMoved
    
    def legal_moves(self):
        return [(x,y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 0 and self.ExistsSandwichedCounter(x,y)]

    def is_adjacent(self,x,y):
        for (dx,dy) in [(0,+1),(+1,+1),(+1,0),(+1,-1),(0,-1),(-1,-1),(-1,0),(-1,+1)]:
            if self.is_valid(x+dx,y+dy) and self.board[x+dx][y+dy] == self.playerJustMoved:
                return True
        return False
    
    def AdjacentEnemyDirections(self,x,y):
        es = []
        for (dx,dy) in [(0,+1),(+1,+1),(+1,0),(+1,-1),(0,-1),(-1,-1),(-1,0),(-1,+1)]:
            if self.is_valid(x+dx,y+dy) and self.board[x+dx][y+dy] == self.playerJustMoved:
                es.append((dx,dy))
        return es
    
    def ExistsSandwichedCounter(self,x,y):
        for (dx,dy) in self.AdjacentEnemyDirections(x,y):
            if len(self.SandwichedCounters(x,y,dx,dy)) > 0:
                return True
        return False
    
    def GetAllSandwichedCounters(self, x, y):
        sandwiched = []
        for (dx,dy) in self.AdjacentEnemyDirections(x,y):
            sandwiched.extend(self.SandwichedCounters(x,y,dx,dy))
        return sandwiched

    def SandwichedCounters(self, x, y, dx, dy):
        x += dx
        y += dy
        sandwiched = []
        while self.is_valid(x,y) and self.board[x][y] == self.playerJustMoved:
            sandwiched.append((x,y))
            x += dx
            y += dy
        if self.is_valid(x,y) and self.board[x][y] == 3 - self.playerJustMoved:
            return sandwiched
        else:
            return [] 

    def is_valid(self, x, y):
        return x >= 0 and x < self.size and y >= 0 and y < self.size
    
    def weight(self, playerjm):
        jmcount = len([(x,y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == playerjm])
        notjmcount = len([(x,y) for x in range(self.size) for y in range(self.size) if self.board[x][y] == 3 - playerjm])
        if jmcount > notjmcount: 
            return 1.0
        elif notjmcount > jmcount: 
            return 0.0
        else: 
            return 0.5 

    def __repr__(self):
        s= ""
        for y in range(self.size-1, -1, -1):
            for x in range(self.size):
                s += ".XO"[self.board[x][y]]
            s += "\n"
        return s

class Node:
    def __init__(self, move = None, parent = None, state = None):
        self.move = move 
        self.parentNode = parent 
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.untriedMoves = state.legal_moves() 
        self.playerJustMoved = state.playerJustMoved 
        
    def get_child(self):
        s = sorted(self.childNodes, key = lambda c: c.wins/c.visits + sqrt(2*log(self.visits)/c.visits))[-1]
        return s
    
    def add_child(self, m, s):
        n = Node(move = m, parent = self, state = s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)
        return n
    
    def Update(self, result):
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(self.untriedMoves) + "]"

    def TreeToString(self, indent):
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
             s += c.TreeToString(indent+1)
        return s

    def IndentString(self,indent):
        s = "\n"
        for i in range (1,indent+1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
             s += str(c) + "\n"
        return s


def monte_carlo(rootstate, itermax, verbose = False):
    rootnode = Node(state = rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.Clone()

        while node.untriedMoves == [] and node.childNodes != []: 
            node = node.get_child()
            state.make_move(node.move)

        if node.untriedMoves != []: 
            m = random.choice(node.untriedMoves) 
            state.make_move(m)
            node = node.add_child(m,state) 

        while state.legal_moves() != []: 
            state.make_move(random.choice(state.legal_moves()))

        # backprop
        while node != None: 
            node.Update(state.weight(node.playerJustMoved)) 
            node = node.parentNode

    if (verbose):
        print rootnode.TreeToString(0)
    else: 
        print rootnode.ChildrenToString()

    return sorted(rootnode.childNodes, key = lambda c: c.visits)[-1].move 
                
def game():
    board = OthelloState(8)     
    while (board.legal_moves() != []):
        print str(board)
        if board.playerJustMoved == 1:
            m = monte_carlo(rootstate = board, itermax = 1000, verbose = False) 
        else:
            m = monte_carlo(rootstate = board, itermax = 100, verbose = False)
        print "Best Move: " + str(m) + "\n"
        board.make_move(m)
    if board.weight(board.playerJustMoved) == 1.0:
        print "Player " + str(board.playerJustMoved) + " wins!"
    elif board.weight(board.playerJustMoved) == 0.0:
        print "Player " + str(3 - board.playerJustMoved) + " wins!"
    else: 
        print "tie"

if __name__ == "__main__":
    game()

            
                          
            

