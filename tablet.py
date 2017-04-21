# tablet.py
# implements tablet mode

import g # esp g.green (cell)
import utils,pygame

def draw():
    d=g.sy(.2)
    x=g.green.x; y=g.green.y; s=g.dd
    pygame.draw.rect(g.screen,utils.GREEN,(x,y,s,s),d)

def mouse():
    g.pos=mid(); pygame.mouse.set_pos(g.pos)

def left():
    r=g.green.r; c=g.green.c
    c-=1
    if c<0: c=7
    g.green=g.cells[8*r+c]; mouse()

def right():
    r=g.green.r; c=g.green.c
    c+=1
    if c>7: c=0
    g.green=g.cells[8*r+c]; mouse()

def up():
    r=g.green.r; c=g.green.c
    r-=1
    if r<0: r=7
    g.green=g.cells[8*r+c]; mouse()

def down():
    r=g.green.r; c=g.green.c
    r+=1
    if r>7: r=0
    g.green=g.cells[8*r+c]; mouse()

def mid():
    x=g.green.x+g.d2; y=g.green.y+g.d2
    return (x,y)


    


    
