# menu_tablet.py

import buttons,g,pygame,utils,g

def draw():
    d=g.sy(.1)
    x,y=buttons.xy(str(g.menu_green)); x-=d; y-=d; s=buttons.w('1')+d+d
    pygame.draw.rect(g.screen,utils.GREEN,(x,y,s,s),d)

def mouse():
    x,y=buttons.xy(str(g.menu_green))
    g.pos=(x+g.d2,y+g.d2); pygame.mouse.set_pos(g.pos)

def right():
    r,c=rc(); c+=1
    if c==6: c=0
    n=6*r+c+1
    if buttons.active(str(n)): g.menu_green=n; mouse()
    
def left():
    r,c=rc(); c-=1
    if c<0: c=5
    n=6*r+c+1
    if buttons.active(str(n)): g.menu_green=n; mouse()
    
def down():
    r,c=rc(); r+=1
    if r==3: r=0
    n=6*r+c+1
    if buttons.active(str(n)): g.menu_green=n; mouse()
    
def up():
    r,c=rc(); r-=1
    if r<0: r=2
    n=6*r+c+1
    if buttons.active(str(n)): g.menu_green=n; mouse()
    
def rc():
    r=(g.menu_green-1)/6; c=(g.menu_green-1)-6*r
    return r,c
