#!/usr/bin/python
# EndGame.py
"""
    Copyright (C) 2011  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,pygame,utils,sys,load_save,buttons,tablet,menu_tablet,chess
try:
    import gtk
except:
    pass

class EndGame:

    def __init__(self):
        self.journal=True # set to False if we come in via main()
        self.canvas=None # set to the pygame canvas if we come in via activity.py

    def display(self):
        if g.menu:
            g.screen.fill((125,0,0))
            g.screen.blit(g.bgd,(g.offset,0))
            self.menu_hide()
            menu_tablet.draw()
        elif g.help1:
            g.screen.fill((0,0,124))
            self.chess.help1()
        else:
            g.screen.fill((192,255,255))
            self.chess.draw()
            if g.state in (1,2): tablet.draw()
            if self.chess.layout>6: # draw black/white "whose move?" circle
                img=None
                if g.state==1: img=g.w_img
                if g.state==2: img=g.b_img
                if g.state==6: img=g.smile
                if g.state==7: img=g.frown
                if img!=None: utils.centre_blit(g.screen,img,g.bw)
            if self.chess.layout not in (11,13,15,17):
                l=self.chess.layout
                s=self.chess.layout_scores[l]
                both=False
                if g.top==19 or g.top>l: both=True
                img=g.ghost
                for ind in range(2):
                    if ind==0:
                        if s>0 or both: img=g.star
                    else:
                        if s==1 and not both: img=g.ghost
                    utils.centre_blit(g.screen,img,g.star_c[ind])
        buttons.draw()

    def do_click(self):
        if g.menu: return False
        return self.chess.left_click()

    def do_button(self,bu):
        for n in range(1,19):
            if bu==str(n):
                self.chess.set_layout(n); self.chess.setup()
                for b in range(1,19): buttons.off(str(b))
                buttons.on(['menu','new'])
                if self.chess.layout in self.chess.help: buttons.on('help')
                g.menu=False; return
        if bu=='menu': self.menu(); return
        if bu=='help':
            if g.help1: g.help1=False; buttons.on('new')
            else: self.help1()
        if bu=='new':
            self.chess.setup()

    def menu(self):
        for b in range(1,19):
            buttons.on(str(b))
            if b==g.top: break
        buttons.off(['menu','help','new'])
        g.menu=True; g.help1=False

    def help1(self):
        for b in range(1,19): buttons.off(str(b))
        buttons.off('new')
        g.help1=True
        
    def do_key(self,key):
        if g.menu:
            if key in g.LEFT: menu_tablet.left(); return
            if key in g.RIGHT: menu_tablet.right(); return
            if key in g.UP: menu_tablet.up(); return
            if key in g.DOWN: menu_tablet.down(); return
            if key in g.CROSS: self.do_button(str(g.menu_green)); return
        elif g.help1:
            if key in g.TICK: self.do_button('help'); return
        else:
            if key in g.LEFT: tablet.left(); return
            if key in g.RIGHT: tablet.right(); return
            if key in g.UP: tablet.up(); return
            if key in g.DOWN: tablet.down(); return
            if key in g.CROSS:
                keep=g.pos; g.pos=tablet.mid()
                self.do_click(); g.pos=keep; return
            if key in g.SQUARE: self.do_button('new'); return
            if key in g.TICK: self.do_button('help'); return
        if key in g.CIRCLE: self.do_button('menu'); return
        if key==pygame.K_v: g.version_display=not g.version_display; return
        #if key==pygame.K_1: print self.chess.swap###

    def update(self):
        if g.state==2:
            pygame.time.wait(1000); g.state=3; return
        if g.state==3:
            self.chess.black(); g.redraw=True
            if g.state==3: g.state=1
            return

    def buttons_setup(self):
        cy=g.sy(5.8); dx=g.sy(4.87); dy=g.sy(7.1); n=1
        for r in range(3):
            cx=g.sx(3.82)
            for c in range(6):
                buttons.Button(str(n),(cx,cy),colour='yellow')
                buttons.off(str(n))
                cx+=dx; n+=1
            cy+=dy
        cx,cy=g.sx(29),g.h-g.sy(7.2); dy=g.sy(3.5)
        buttons.Button('menu',(cx,cy))
        buttons.Button('help',(g.sy(3),cy)); cy+=dy
        buttons.Button('new',(cx,cy),colour='cyan')
        g.bw=(g.sy(3),cy)
        k=g.sy(3); g.star_c=[(k+g.offset,k),(g.w-k+g.offset,k)]
        self.menu()
        
    def menu_hide(self):
        dx=g.sy(1.5); dy=g.sy(4.6); colr=(0,125,125); w=g.sy(5.5); h=g.sy(4.5)
        for layout in range(1,19):
            if layout>g.top:
                x,y=buttons.xy(str(layout)); x-=dx; y-=dy 
                pygame.draw.rect(g.screen,colr,(x,y,w,h))
                
    def flush_queue(self):
        flushing=True
        while flushing:
            flushing=False
            if self.journal:
                while gtk.events_pending(): gtk.main_iteration()
            for event in pygame.event.get(): flushing=True

    def run(self):
        g.init()
        if not self.journal: utils.load()
        self.chess=chess.Chess()
        g.cells=self.chess.cells
        load_save.retrieve()
        self.chess.setup() # having retrieved layout if any
        self.buttons_setup()
        if self.canvas<>None: self.canvas.grab_focus()
        ctrl=False
        pygame.key.set_repeat(600,120); key_ms=pygame.time.get_ticks()
        going=True
        while going:
            if self.journal:
                # Pump GTK messages.
                while gtk.events_pending(): gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.pos=event.pos
                    g.redraw=True
                    if self.canvas<>None: self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==1:
                        if self.do_click():
                            pass
                        else:
                            bu=buttons.check()
                            if bu!='': self.do_button(bu); self.flush_queue()
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms>110:
                        key_ms=pygame.time.get_ticks()
                        if ctrl:
                            if event.key==pygame.K_q:
                                if not self.journal: utils.save()
                                going=False; break
                            else:
                                ctrl=False
                        if event.key in (pygame.K_LCTRL,pygame.K_RCTRL):
                            ctrl=True; break
                        self.do_key(event.key); g.redraw=True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl=False
            if not going: break
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                g.screen.blit(g.pointer,g.pos)
                pygame.display.flip()
                g.redraw=False
            self.update()
            g.clock.tick(40)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((1024,768),pygame.FULLSCREEN)
    game=EndGame()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
