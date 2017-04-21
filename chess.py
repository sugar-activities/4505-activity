# chess.py
import g,utils,random,pygame,chessh

# computer always plays black

class Cell:
    def __init__(self,x,y,r,c,white):
        self.x=x; self.y=y; self.r=r; self.c=c; self.white=white
        self.piece=None # pieces numbered 0 to 11
        self.number=None

class Chess:
    def __init__(self):
        # layouts
        # 1  2  3  4  5  6   7   8   9   10  11  12  13  14  15  16  17  18
        # P, K ,R, Q, N, B,  RB, BN, NQ, QR, RR, RR, KQ, KQ, KP, KP, KR, KR
        self.layout_scores=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        # numbered from 0 to 18
        pieces=['wp','wn','wb','wr','wq','wk','bp','bn','bb','br','bq','bk']
        self.help=[1,2,3,4,5,6,12,14,18]
        self.imgs=[]; self.glow=[]
        for piece in pieces:
            img=utils.load_image(piece+'.png',True,'pieces')
            self.imgs.append(img)
            img=utils.load_image(piece+'.png',True,'glow')
            self.glow.append(img)
        self.cells=[]
        y=g.y0; white=True
        for r in range(8):
            x=g.x0
            for c in range(8):
                cell=Cell(x,y,r,c,white); self.cells.append(cell)
                x+=g.dd; white=not white
            y+=g.dd; white=not white
        #
        g.green=self.cells[36]
        #
        self.nos=[None]; self.nos_yellow=[None]; self.nos_red=[None]
        for n in range(1,10):
            img=utils.load_image(str(n)+'.png',True,'numbers')
            self.nos.append(img)
            img=utils.load_image(str(n)+'.png',True,'yellow')
            self.nos_yellow.append(img)
            img=utils.load_image(str(n)+'.png',True,'red')
            self.nos_red.append(img)
        self.wmate=utils.load_image('wmate.png',True)
        self.bmate=utils.load_image('bmate.png',True)
        self.stale=utils.load_image('stale.png',True)
        self.help_imgs=[]
        for n in range(19): # layout nos
            img=None
            if n in self.help:
                img=utils.load_image(str(n)+'.png',True,'help')
            self.help_imgs.append(img)
        self.layout=1; self.swap=False # used in set2() for one2one

    def setup(self):
        for cell in self.cells: cell.piece=None; cell.number=None
        self.selected=None; self.wrong=[]
        if self.layout==12: p1=3; p2=3 # 2 rooks
        elif self.layout==14: p1=5; p2=4 # K & Q
        elif self.layout==18: p1=5; p2=3 # K & R
        if self.layout in (12,14,18):
            r=random.randint(3,4); c=random.randint(3,4); self.set1(r,c,11) # BK
            r1=random.randint(0,1); c1=random.randint(0,7)
            r2=random.randint(6,7); c2=random.randint(0,7)
            if random.randint(0,1)==1:
                r1=random.randint(0,7); c1=random.randint(0,1)
                r2=random.randint(0,7); c2=random.randint(6,7)
            self.set1(r1,c1,p1); self.set1(r2,c2,p2)
            g.state=2 # B to move - in case already in check
        if self.layout==16: # K & P
            r=random.randint(0,7); c=random.randint(0,2); self.set1(r,c,11)
            r=random.randint(0,7); c=random.randint(5,7); self.set1(r,c,5) # WK
            c=random.randint(3,4); self.set1(6,c,0) # WP
            self.pawn_cell=self.get_cell(0,c)
            g.state=1
        if self.layout==1: self.numbers_pawn() # pawn path
        if self.layout==2: self.numbers(5) # king path
        if self.layout==3: self.numbers(3) # rook path
        if self.layout==4: self.numbers(4) # queen path
        if self.layout==5: self.numbers(1) # knight path
        if self.layout==6: self.numbers(2) # bishops path
        if self.layout<7: self.aim=1; g.state=1 # paths
        self.checked=False; self.promoted=False
        if self.layout in (7,8,9,10): self.set2()
        if self.layout==11: self.rr_move=0; self.rr(); g.state=1 #RR
        if self.layout==13: self.kq_move=0; self.kq(); g.state=1 #KQ
        if self.layout==15: self.kp_move=0; self.kp(); g.state=1 #KQ
        if self.layout==17: self.kr_move=0; self.kr(); g.state=1 #KQ

    def draw(self):
        g.screen.blit(g.board,(g.x0-g.border,g.y0-g.border))
        for cell in self.cells:
            if cell.piece!=None:
                if cell!=self.selected:
                    if self.layout<7 and self.aim==10:
                        pass
                    else:
                        img=self.imgs[cell.piece]
                        x=cell.x+g.d2-img.get_width()/2
                        y=cell.y+g.dd-img.get_height()-g.base
                        g.screen.blit(img,(x,y))
            self.draw_number(cell)
        if self.selected!=None:
            cell=self.selected
            if cell.piece!=None:
                img=self.glow[cell.piece]
                x=cell.x+g.d2-img.get_width()/2
                y=cell.y+g.dd-img.get_height()-g.base+g.glow
                if self.layout<7 and self.aim==10:
                    pass
                elif self.layout==1 and self.aim==6:
                    pass
                else:
                    g.screen.blit(img,(x,y))
            self.draw_number(cell)
        if self.layout>9: #games
            img=None
            if g.state==4:
                if utils.odd(self.layout): img=self.wmate
                else: img=self.bmate
            if g.state==5: img=self.stale
            if img!=None: utils.centre_blit(g.screen,img,g.centre)
        self.check() # manage successes & top
             
    def draw_number(self,cell):
        if cell.number!=None:
            cx=cell.x+g.d2; cy=cell.y+g.d2; img=self.nos[cell.number]
            if cell.number==self.aim: img=self.nos_yellow[cell.number]
            if self.aim==10: img=self.nos_yellow[cell.number]
            if self.layout==1 and self.aim==6:
                img=self.nos_yellow[cell.number]
            if cell.number in self.wrong: img=self.nos_red[cell.number]
            utils.centre_blit(g.screen,img,(cx,cy))
        
    def left_click(self):
        if g.state!=1 and self.layout!=6: return
        cell=self.which()
        if cell!=None: # have clicked cell
            if self.layout<7: # number chase
                if self.aim==10: return
                if self.layout==1 and self.aim==6: return
                if self.layout==6:
                    if cell.piece==2: self.selected=cell; return
                if chessh.legal(self.selected,cell):
                    if chessh.move(self.selected,cell):
                        self.check_number(self.selected,cell)
                        if self.wrong!=[]: self.aim=1
                        self.selected=cell
                return   
            if cell==self.selected: self.selected=None; return True
            if self.selected!=None: 
                if cell.piece==None or self.layout in (7,8,9,10,11,13,15,17):
                    if self.layout==10:
                        if cell.piece!=None:
                            if chessh.colour(cell.piece)=='w':
                                self.selected=cell; return True
                    # make move if possible
                    if chessh.legal(self.selected,cell):
                        pce=self.selected.piece
                        # move successful only if no check remains
                        if chessh.move(self.selected,cell):
                            self.selected=None
                            if self.layout==9:
                                if cell.piece!=pce: self.promoted=True
                            if self.layout>6: g.state=2
                    return True
            if cell.piece>5: return True # can't select black piece
            if cell.piece!=None: self.selected=cell
            return True
        return False # didn't click on square

    def check(self): # manage successes & top
        if self.checked: return
        success=False
        if self.layout in (11,13,15,17):
            success=True
        elif self.layout>10: # game
            if g.state==4: success=True
        elif self.layout>6: # one2one
            if g.state==6: success=True
        else: # numbers path
            if self.layout==1 and self.aim==6: success=True
            elif self.aim==10: success=True
        if success:
            if  self.layout_scores[self.layout]<2:
                self.layout_scores[self.layout]+=1
                if self.layout_scores[self.layout]==2:
                    if g.top<19:
                        if g.top==self.layout: g.top+=1
            if self.layout in (7,8,9,10): self.swap=not self.swap
            self.checked=True
                
    def set1(self,r,c,piece):
        cell=self.get_cell(r,c)
        cell.piece=piece

    # wp wn wb wr wq wk   bp bn bb br bq bk
    #  0  1  2  3  4  5    6  7  8  9 10 11

    def set2(self): # used to setup one on one battles
        g.state=1
        if self.layout==10:
            for c in range(4):
                self.set1(1,c,6); self.set1(6,c,0)
            return
        if self.layout==7: p1,p2=3,8
        elif self.layout==8: p1,p2=2,7
        elif self.layout==9: p1,p2=1,10
        if self.swap:
            p1+=6
            if p1>11:p1-=12
            p2+=6
            if p2>11:p2-=12
        r=random.randint(0,2); c=random.randint(0,2); self.set1(r,c,p1)
        r=random.randint(5,7); c=random.randint(5,7); self.set1(r,c,p2)
        
    def check_number(self,cell1,cell2):
        self.wrong=[]
        if self.layout>6: return
        if self.layout==5: #Knight
            if cell2.number==None: return
            if cell2.number!=self.aim: self.wrong.append(cell2.number)
            else: self.aim+=1
            return
        dr=utils.sign(cell2.r-cell1.r); dc=utils.sign(cell2.c-cell1.c)
        r=cell1.r; c=cell1.c
        for i in range(7):
            r+=dr; c+=dc; cell=chessh.get_cell(r,c)
            if cell.number!=None:
                if cell.number!=self.aim: self.wrong.append(cell.number)
                else: self.aim+=1
            if dr!=0 and r==cell2.r: return
            if dc!=0 and c==cell2.c: return

    def which(self):
        for cell in self.cells:
            if utils.mouse_in(cell.x,cell.y,cell.x+g.dd,cell.y+g.dd):
                return cell
        return None

    def dist(self,cell1,cell2=None): # manhattan distance of cell1 from cell2
        if cell2==None: # do distance from centre
            return abs(float(cell1.r)-3.5)+abs(float(cell1.c)-3.5)
        return abs(cell1.r-cell2.r)+abs(cell1.c-cell2.c)
    
    def get_mates(self,cell): # cells adjacent to cell - ie K possible moves
        r0=cell.r; c0=cell.c
        mates=[]
        r=r0-1; c=c0
        if r>=0: mates.append(self.cells[r*8+c])
        r=r0+1; c=c0
        if r<8: mates.append(self.cells[r*8+c])
        r=r0; c=c0-1
        if c>=0: mates.append(self.cells[r*8+c])
        r=r0; c=c0+1
        if c<8: mates.append(self.cells[r*8+c])
        r=r0-1; c=c0-1
        if r>=0 and c>=0: mates.append(self.cells[r*8+c])
        r=r0+1; c=c0-1
        if r<8 and c>=0: mates.append(self.cells[r*8+c])
        r=r0-1; c=c0+1
        if r>=0 and c<8: mates.append(self.cells[r*8+c])
        r=r0+1; c=c0+1
        if r<8 and c<8: mates.append(self.cells[r*8+c])
        return mates

    def black(self):
        if self.layout in (7,8,9): self.one2one(); return
        if self.layout==10: self.pppp(); return # PPPP
        if self.layout==11: self.rr(); return # RR
        if self.layout==13: self.kq(); return # KQ
        if self.layout==15: self.kp(); return # KP
        if self.layout==17: self.kr(); return # KR
        # will only be moving a Black King in 12,14,16,18
        # find bk
        for cell in self.cells:
            if cell.piece==11: break
        bk=cell
        mates=self.get_mates(bk)
        pce=bk.piece; bk.piece=None
        attacked=chessh.attack('w'); bk.piece=pce
        # check for unprotected piece to take
        for cell in mates:
            if cell.piece!=None:
                if cell not in attacked:
                    cell.piece=bk.piece; bk.piece=None; return
        # move towards centre if possible
        dmin=100; cell1=None
        for cell in mates:
            if cell not in attacked:
                d=self.dist(cell)
                if d<dmin: dmin=d; cell1=cell
        if cell1==None: # nowhere to move
            if bk in attacked: g.state=4; return # mate
            else: g.state=5; return # stale
        if self.layout in (12,18):
            # chase closest rook
            rooks=[] # find rook(s)
            for cell in self.cells:
                if cell.piece==3: rooks.append(cell)
            dmin=100; cell1=None
            for cell in mates:
                if cell not in attacked:
                    for cell2 in rooks:
                        d=self.dist(cell,cell2)
                        if d<dmin: dmin=d; cell1=cell
        if self.layout==16:
            if False: # chase pawn - not implemented
                pawn=None
                for cell in self.cells:
                    if cell.piece==0: pawn=cell; break
                if pawn!=None:
                    dmin=100; cell1=None
                    for cell in mates:
                        if cell not in attacked:
                            d=self.dist(cell,pawn)
                            if d<dmin: dmin=d; cell1=cell
            else: # head for blocking square
                dmin=100; cell1=None
                for cell in mates:
                    if cell not in attacked:
                        d=self.dist(cell,self.pawn_cell)
                        if d<dmin: dmin=d; cell1=cell
        chessh.move(bk,cell1)
            
    def numbers(self,piece):
        last=10; pce2=None
        if piece==2: last=11
        sqs=range(16); random.shuffle(sqs); sqs=sqs[:last]; pce=sqs.pop()
        if piece==2:
            pce2=sqs.pop()
            if pce>pce2: pce2,pce=pce,pce2 # ensure we do pce first
        r1=0; sq=0
        for r0 in range(4):
            c1=0
            for c0 in range(4):
                if sq in sqs:
                    n=sqs.index(sq)+1
                    r=random.randint(r1,r1+1); c=random.randint(c1,c1+1)
                    cell=self.get_cell(r,c); cell.number=n
                    n+=1
                elif sq==pce:
                    r=random.randint(r1,r1+1); c=random.randint(c1,c1+1)
                    cell=self.get_cell(r,c); cell.piece=piece
                    self.selected=cell; cell1=cell
                elif sq==pce2:
                    while True:
                        r=random.randint(r1,r1+1); c=random.randint(c1,c1+1)
                        cell=self.get_cell(r,c)
                        if cell.white!=cell1.white: break
                    cell.piece=piece; self.selected=cell
                sq+=1
                c1+=2
            r1+=2

    def numbers_pawn(self):
        c=random.randint(0,7)
        cell=self.get_cell(6,c); cell.piece=0; self.selected=cell
        n=5
        for r in range(5):
            cell=self.get_cell(r,c); cell.number=n; n-=1

    def set_layout(self,n):
        self.layout=n

    def help1(self):
        img=self.help_imgs[self.layout]
        if img==None: return
        if self.layout>6:
            utils.centre_blit(g.screen,img,g.centre)
        else:
            g.screen.blit(img,(g.offset,0))

    # wp wn wb wr wq wk   bp bn bb br bq bk
    #  0  1  2  3  4  5    6  7  8  9 10 11

    # KP end game with computer playing black
    def kp(self):
        if self.kp_move==0:
            for (r,c,p) in [(7,6,11),(1,3,6),(7,0,5)]: self.set1(r,c,p)
            self.bk=self.get_cell(7,6)
            self.bp=self.get_cell(1,3)
            self.kp_move+=1
        elif self.kp_move==1:
            ncell=self.get_cell(6,5)
            chessh.move(self.bk,ncell)
            self.bk=ncell; self.kp_move+=1
            g.state=1
        elif self.kp_move==2:
            ncell=self.get_cell(5,4)
            chessh.move(self.bk,ncell)
            self.bk=ncell; self.kp_move+=1
            g.state=1
        elif self.kp_move==3:
            ncell=self.get_cell(4,4)
            chessh.move(self.bk,ncell)
            self.bk=ncell; self.kp_move+=1
            g.state=1
        elif self.kp_move==4:
            ncell=self.get_cell(3,3)
            chessh.move(self.bp,ncell)
            self.bp=ncell; self.kp_move+=1
            g.state=1
        else:
            g.state=1
            # find WK
            for cell in self.cells:
                if cell.piece==5: break
            wk=cell
            done=False
            if self.dist(self.bp,self.bk)>2: # move bk towards bp
                dr=self.bp.r-self.bk.r # v28
                ncell=self.get_cell(self.bk.r+dr,self.bk.c) # v28 - was r-1
                if ncell!=None: # v 28 extra cautious :o)
                    chessh.move(self.bk,ncell); self.bk=ncell
                    done=True
            if not done:
                ncell=self.get_cell(self.bp.r+1,self.bp.c) # advance pawn?
                if ncell.piece==None: # cell is empty but ...
                    # don't move if new square under attack and not protected
                    attacked=chessh.attack('w')
                    if ncell in attacked: # under attack - protected?
                        mates=self.get_mates(self.bk)
                        if ncell in mates: # protected so move
                            chessh.move(self.bp,ncell); self.bp=ncell; done=True
                    else: # not under attack so move
                        chessh.move(self.bp,ncell); self.bp=ncell; done=True
            if not done: # unable to safely move pawn
                ncell=self.get_cell(self.bk.r+1,self.bk.c) # advance King?
                if self.bk_ok(self.bk,ncell): # ok so move
                    chessh.move(self.bk,ncell); self.bk=ncell; done=True
            if not done: # move King sideways towards WK
                dc=utils.sign(wk.c-self.bk.c)
                ncell=self.get_cell(self.bk.r,self.bk.c+dc)
                if self.bk_ok(self.bk,ncell): # ok so move
                    chessh.move(self.bk,ncell); self.bk=ncell; done=True
                else: # move in opposite direction
                    ncell=self.get_cell(self.bk.r,self.bk.c-dc)
                    if self.bk_ok(self.bk,ncell): # ok so move
                        chessh.move(self.bk,ncell); self.bk=ncell; done=True
            if not done: print 'ouch!'
            if self.bp.r==7: self.bp.piece=10; g.state=7
            # check for stalemate
            self.check_wk(wk) # will set g.state if necessary

    def bk_ok(self,cell1,cell2): # ok to move bk from cell1 to cell2?
        if chessh.colour(cell2.piece)=='b': return False # own piece there
        pce=cell1.piece; cell1.piece=None # get piece out of raod of test
        attacked=chessh.attack('w'); cell1.piece=pce
        if cell2 in attacked: return False # can't move into check
        return True

    # KR end game with computer playing black
    def kr(self):
        if self.kr_move==0:
            for (r,c,p) in [(1,5,11),(3,6,9),(6,7,5)]: self.set1(r,c,p)
            self.bk=self.get_cell(1,5)
            self.br=self.get_cell(3,6)
            self.kr_move+=1
        elif self.kr_move==1:
            ncell=self.get_cell(self.bk.r+1,self.bk.c)
            chessh.move(self.bk,ncell); self.bk=ncell; g.state=1
            self.kr_move+=1
        else:
            g.state=1
            # find WK
            for cell in self.cells:
                if cell.piece==5: break
            wk=cell
            done=False
            if not done: # 2nd last posn?
                if self.br.r==5 and self.bk.r==6 and wk.r==6:
                    ncell=self.get_cell(self.br.r,self.br.c-1)
                    chessh.move(self.br,ncell); self.br=ncell; done=True
            if not done: # final posn?
                if self.br.r==5 and self.bk.r==6 and wk.r==7:
                    ncell=self.get_cell(self.br.r,7)
                    chessh.move(self.br,ncell); self.br=ncell; done=True
            if not done:
                if self.bk.r<self.br.r: # BK trailing
                    ncell=self.get_cell(self.bk.r+1,self.bk.c)
                    chessh.move(self.bk,ncell); self.bk=ncell; done=True
            if not done:
                if self.br.r<self.bk.r: # BR trailing
                    if self.br.r<5:
                        ncell=self.get_cell(self.br.r+1,self.br.c)
                        chessh.move(self.br,ncell); self.br=ncell; done=True
            if not done: # must be level or on row 5
                if (self.bk.r+1)==wk.r or self.br.r==5: # move BK
                    ncell=self.get_cell(self.bk.r+1,self.bk.c)
                    chessh.move(self.bk,ncell); self.bk=ncell; done=True
                else: # move BR
                    ncell=self.get_cell(self.br.r+1,self.br.c)
                    chessh.move(self.br,ncell); self.br=ncell; done=True
            self.kr_move+=1
            self.check_wk(wk) # will set g.state if necessary

    def check_wk(self,wk): # on cell wk
        # find WK mates
        mates=self.get_mates(wk) # ie the squares WK can move to
        wk.piece=None
        attacked=chessh.attack('b') # get attacked
        wk.piece=5
        for cell in mates:
            if cell not in attacked: return # WK can move
        # no moves for WK
        if wk in attacked: g.state=4 # checkmate
        else: g.state=5 # stalemate

    # KQ end game with computer playing black queen
    def kq(self):
        if self.kq_move==0:
            for (r,c,p) in [(1,5,11),(3,3,10),(6,7,5)]: self.set1(r,c,p)
            self.bk=self.get_cell(1,5)
            self.bq=self.get_cell(3,3)
            self.kq_move+=1
        elif self.kq_move==1:
            ncell=self.get_cell(3,5); chessh.move(self.bq,ncell)
            self.bq=ncell; self.kq_move+=1
            g.state=1
        elif self.kq_move==2:
            ncell=self.get_cell(2,6); chessh.move(self.bk,ncell)
            self.bk=ncell; self.kq_move+=1
            g.state=1
        else:
            g.state=1
            # find WK
            for cell in self.cells:
                if cell.piece==5: break
            wk=cell
            # ready to mate?
            if wk.r==7 and self.bq.r==6 and self.bk.r==5: #yes!
                if abs(wk.c-self.bk.c)<2:
                    ncell=self.get_cell(6,wk.c)
                    chessh.move(self.bq,ncell); self.bq=ncell
                else:
                    dc=utils.sign(wk.c-self.bk.c)
                    ncell=self.get_cell(self.bk.r,self.bk.c+dc)
                    chessh.move(self.bk,ncell); self.bk=ncell
            # if WK on row 7 move BQ to row 6
            elif wk.r==7 and self.bq.r!=6:
                r=self.bq.r; c=self.bq.c
                for i in range(7):
                    r+=1; c-=1
                    if r==6: break
                ncell=self.get_cell(r,c)
                chessh.move(self.bq,ncell); self.bq=ncell
            else:
                # move BK down if poss, else move BQ down
                attacked=chessh.attack('w') # fetch no go squares
                ncell=self.get_cell(self.bk.r+1,self.bk.c)
                if ncell in attacked:
                    dc=0
                    if self.bq.r==5: dc=-1
                    ncell=self.get_cell(self.bq.r+1,self.bq.c+dc)
                    chessh.move(self.bq,ncell); self.bq=ncell
                else:
                    chessh.move(self.bk,ncell); self.bk=ncell
            self.kq_move+=1
            self.check_wk(wk)

    # RR end game with computer playing black rooks
    def rr(self):
        if self.rr_move==0:
            for (r,c,p) in [(0,6,9),(5,2,5),(6,0,9)]: self.set1(r,c,p)
            self.rcell1=self.get_cell(0,6)
            self.rcell2=self.get_cell(6,0)
            self.rr_move+=1
        elif self.rr_move==1:
            ncell=self.get_cell(6,7); chessh.move(self.rcell2,ncell)
            self.rcell2=ncell; self.rr_move+=1
            g.state=1
        else:
            g.state=1
            for cell in self.cells: # find WK
                if cell.piece==5: wk=cell; break
            if abs(self.rcell1.r-wk.r)<2:
                r=7
                if self.rcell1.r==7: r=0 
                ncell=self.get_cell(r,self.rcell1.c)
                chessh.move(self.rcell1,ncell); self.rcell1=ncell
            elif abs(self.rcell2.r-wk.r)<2:
                r=6
                if self.rcell2.r==6: r=1 
                ncell=self.get_cell(r,self.rcell2.c)
                chessh.move(self.rcell2,ncell); self.rcell2=ncell
            else:
                if self.rcell1.c<self.rcell2.c:
                    ncell=self.get_cell(self.rcell2.r,self.rcell2.c-2)
                    chessh.move(self.rcell2,ncell); self.rcell2=ncell
                else:
                    ncell=self.get_cell(self.rcell1.r,self.rcell1.c-2)
                    chessh.move(self.rcell1,ncell); self.rcell1=ncell
                if self.rcell1.c+self.rcell2.c==1:
                    g.state=4 # checkmate

    # wp wn wb wr wq wk   bp bn bb br bq bk
    #  0  1  2  3  4  5    6  7  8  9 10 11

    def one2one(self):
        cellw=None; cellb=None
        for cell in self.cells: # find pieces
            if cell.piece!=None:
                if chessh.colour(cell.piece)=='w': cellw=cell
                if chessh.colour(cell.piece)=='b': cellb=cell
        if cellb==None: g.state=6; return
        attacked=chessh.attack('b')
        # find all the cells I'm (black) is attacking
        if cellw in attacked:
            chessh.move(cellb,cellw); g.state=7; return
        # no capture just make random move
        rnd=random.randint(0,len(attacked)-1)
        chessh.move(cellb,attacked[rnd])
        g.state=1

    def pppp(self):
        cellw=[]; cellb=[]
        for cell in self.cells: # find pieces
            if cell.piece!=None:
                if chessh.colour(cell.piece)=='w': cellw.append(cell)
                if chessh.colour(cell.piece)=='b': cellb.append(cell)
        if cellb==[]: g.state=6; return
        if cellw==[]: g.state=7; return
        ind=random.randint(0,len(cellb)-1)
        for i in range(len(cellb)):
            cell=cellb[ind]; r=cell.r; c=cell.c
            if cell.piece==6: # BP
                for dc in (-1,1):
                    ncell=self.get_cell(r+1,c+dc)
                    if ncell!=None:
                        if ncell.piece!=None:
                            if chessh.colour(ncell.piece)=='w':
                                chessh.move(cell,ncell)
                                if len(cellw)==1: g.state=7
                                return
                if r==1:
                    if self.get_cell(r+1,c).piece==None:
                        ncell=self.get_cell(r+2,c)
                        if ncell.piece==None:
                            chessh.move(cell,ncell); return
                ncell=self.get_cell(r+1,c)
                if ncell.piece==None:
                    chessh.move(cell,ncell); return
            else: # BQ
                ncellk=None
                for (dr,dc) in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                    r1=r; c1=c
                    for i in range(7):
                        r1+=dr; c1+=dc; ncell=self.get_cell(r1,c1)
                        if ncell==None: break
                        if ncell.piece!=None:
                            if chessh.colour(ncell.piece)=='w':
                                chessh.move(cell,ncell)
                                if len(cellw)==1: g.state=7
                                return
                            break # must be a Black piece
                        else:
                            ncellk=ncell
                # no captures found
                if ncellk!=None: chessh.move(cell,ncellk); return
            ind+=1
            if ind==len(cellb): ind=0
        # no possible move - stalemate
        g.state=5

    def get_cell(self,r,c):
        return chessh.get_cell(r,c)
        
            
        


