# chessh.py - chess helper functions
# used also by End Game - copy over

# needs g.cells -> board
import g

# wp wn wb wr wq wk   bp bn bb br bq bk
#  0  1  2  3  4  5    6  7  8  9 10 11

def king_in_check(colr): # currently in check?
    kcell=None
    k=11 # BK
    if colr=='w': k=5 # WK
    for cell in g.cells: # find King
        if cell.piece==k: kcell=cell; break
    if kcell==None: return False # no King = no check!
    attacked=attack(opp_colour(k))
    if kcell in attacked: return True
    return False

def get_cell(r,c):
    # saves checking all over the place
    if r<0 or r>7 or c<0 or c>7: return None 
    return g.cells[8*r+c]

def colour(piece):
    if piece<6: return 'w'
    else: return 'b'

def opp_colour(piece):
    if piece<6: return 'b'
    else: return 'w'

# move piece on cell1 to cell2 provided side does not end up in check
def move(cell1,cell2):
    pce1=cell1.piece; pce2=cell2.piece
    cell2.piece=pce1; cell1.piece=None # try move
    # pawn promotion ?
    if pce1==0 and cell2.r==0: cell2.piece=4
    if pce1==6 and cell2.r==7: cell2.piece=10
    if king_in_check(colour(pce1)):
        cell1.piece=pce1; cell2.piece=pce2 # undo move
        return False
    return True

def castle(rind,kind): # make the castling move if legal
    rcell=g.cells[rind]; kcell=g.cells[kind]; colr=opp_colour(kcell.piece)
    attacked=attack(colr)
    if kcell in attacked: return False # can't castle out of check
    # check in-between cells
    r=rcell.r; c1=rcell.c; c2=kcell.c; dc=-1
    if c1>c2: c1,c2=c2,c1; dc=1
    for c in range(c1+1,c2):
        cell=get_cell(r,c)
        if cell.piece!=None: return False # path not clear
    c=kcell.c
    # check for check
    if get_cell(r,c+dc*2) in attacked: return False # into check
    if get_cell(r,c+dc) in attacked: return False # moving thru check
    # all ok - do castle
    rook=rcell.piece; king=kcell.piece
    get_cell(r,c+dc*2).piece=king; kcell.piece=None
    get_cell(r,c+dc).piece=rook; rcell.piece=None
    return True
    
def attack(colr): # return list of cells attacked by colr (b/w)
    attacked=[]
    for cell in g.cells:
        pce=cell.piece
        if pce != None:
            if colour(pce)==colr:
                r=cell.r; c=cell.c
                if pce in (0,6): # pawn
                    dr=-1
                    if colr=='b': dr=1
                    attacked.append((r+dr,c-1)); attacked.append((r+dr,c+1))
                if pce in (3,4,9,10): # rook or queen - hor & vert
                    for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                        r1=r; c1=c
                        for i in range(7):
                            r1+=dr; c1+=dc; cell=get_cell(r1,c1)
                            if cell==None: break
                            attacked.append((r1,c1))
                            if cell.piece!=None: break
                if pce in (2,4,8,10): # bishop or queen - diag
                    for dr,dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                        r1=r; c1=c
                        for i in range(7):
                            r1+=dr; c1+=dc; cell=get_cell(r1,c1)
                            if cell==None: break
                            attacked.append((r1,c1))
                            if cell.piece!=None: break
                if pce in (1,7): # knight
                    for dr,dc in [(2,1),(1,2),(-2,1),(1,-2),(2,-1),(-1,2),(-2,-1),(-1,-2)]:
                        attacked.append((r+dr,c+dc))
                if pce in (5,11): # king
                    for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        attacked.append((r+dr,c+dc))
    # convert r,c to cell and drop duplicates
    att=[]
    for (r,c) in attacked:
        cell=get_cell(r,c)
        if cell!=None:
            if cell not in att: att.append(cell)
    return att
    
# check move of piece on cell1 to cell2 is ok
# ignores check - this is done in move() function
def legal(cell1,cell2):
    pce1=cell1.piece; pce2=cell2.piece
    if pce2!=None:
        if colour(pce1)==colour(pce2): return False # same colour
    ok=False
    if pce1 in (3,4,9,10): # rook or queen
        if hor_vert(cell1,cell2): ok=True
    if pce1 in (2,4,8,10): # bishop or queen
        if diag(cell1,cell2): ok=True
    if pce1 in (1,7): # knight
        if knight(cell1,cell2): ok=True
    if pce1 in (0,6): # pawn
        if pawn(cell1,cell2): ok=True
    if pce1 in (5,11): # king
        if king(cell1,cell2): ok=True
    return ok
        
# assess whether cell1 to cell2 is possible without obstruction
# just looks at the in-between cells
def hor_vert(cell1,cell2):            
    if cell1.r==cell2.r: # moving along row
        c1=cell1.c; c2=cell2.c; r=cell1.r
        if c1>c2: c1,c2=c2,c1
        for c in range(c1+1,c2):
            cell=get_cell(r,c)
            if cell.piece!=None: return False
        return True
    if cell1.c==cell2.c: # moving along col
        r1=cell1.r; r2=cell2.r; c=cell1.c
        if r1>r2: r1,r2=r2,r1
        for r in range(r1+1,r2):
            cell=get_cell(r,c)
            if cell.piece!=None: return False
        return True
    return False # not hor or vert!

# assess whether cell1 to cell2 is possible without obstruction
# just looks at the in-between cells
def diag(cell1,cell2):            
    if abs(cell1.r-cell2.r) != abs(cell1.c-cell2.c): return False
    c1=cell1.c; c2=cell2.c; r=cell1.r; dr=sign(cell2.r-cell1.r)
    if c1>c2: c1,c2=c2,c1; r=cell2.r; dr=-dr
    for c in range(c1+1,c2):
        r+=dr
        cell=get_cell(r,c)
        if cell.piece!=None: return False
    return True

# check is an ok knight move
def knight(cell1,cell2):
    dr=abs(cell1.r-cell2.r); dc=abs(cell1.c-cell2.c)
    if (dr,dc) in [(1,2),(2,1)]: return True
    return False

# check is an ok pawn move
def pawn(cell1,cell2):
    pce1=cell1.piece; pce2=cell2.piece
    dr=abs(cell1.r-cell2.r); dc=abs(cell1.c-cell2.c)
    if dc>1: return False
    if dc==1: # must be a capture
        if dr<>1: return False
        if pce2==None: return False # no piece to capture
        return True
    # have dc=0
    if pce2!=None: return False # can only take diagonally
    if pce1==6: r0=1; dr0=1 # black pawn
    else: r0=6; dr0=-1 # white pawn
    if dr>2: return False
    if dr>1: # trying double move
        if cell1.r!=r0: return False # not on starting row
        if get_cell(r0+dr0,cell1.c).piece!=None:
            return False # blocking piece
        return True
    if (cell2.r-cell1.r)<>dr0: return False # wrong direction
    return True

# check is an ok king move - ignoring check
def king(cell1,cell2):
    dr=abs(cell1.r-cell2.r); dc=abs(cell1.c-cell2.c)
    if (dr,dc) in [(1,0),(0,1),(1,1)]: return True
    return False

def sign(n):
    if n<0: return -1
    return 1


