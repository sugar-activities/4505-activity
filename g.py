# g.py - globals
import pygame,utils,random

app='End Game'; ver='1'
ver='22'
# layout order rationalised, redeal button added
ver='23'
# 18 tasks instead of 10
ver='24'
# green frame standardised
ver='25'
# numbers - one extra step needed
ver='26'
# star display bug fixed esp on 18
# green square fixed
# layouts 7,8,9 - swapping bug fixed
ver='27'
# pointer follows green frame
ver='28'
# bug in game 15 - line 415 in chess.py

UP=(264,273)
DOWN=(258,274)
LEFT=(260,276)
RIGHT=(262,275)
CROSS=(259,120)
CIRCLE=(265,111)
SQUARE=(263,32)
TICK=(257,13)
NUMBERS={pygame.K_1:1,pygame.K_2:2,pygame.K_3:3,pygame.K_4:4,\
           pygame.K_5:5,pygame.K_6:6,pygame.K_7:7,pygame.K_8:8,\
           pygame.K_9:9,pygame.K_0:0}

def init(): # called by run()
    random.seed()
    global redraw
    global screen,w,h,font1,font2,clock
    global factor,offset,imgf,message,version_display
    global pos,pointer
    redraw=True
    version_display=False
    screen = pygame.display.get_surface()
    pygame.display.set_caption(app)
    screen.fill((70,0,70))
    pygame.display.flip()
    w,h=screen.get_size()
    if float(w)/float(h)>1.5: #widescreen
        offset=(w-4*h/3)/2 # we assume 4:3 - centre on widescreen
    else:
        h=int(.75*w) # allow for toolbar - works to 4:3
        offset=0
    factor=float(h)/24 # measurement scaling factor (32x24 = design units)
    imgf=float(h)/900 # image scaling factor - all images built for 1200x900
    clock=pygame.time.Clock()
    if pygame.font:
        t=int(40*imgf); font1=pygame.font.Font(None,t)
        t=int(72*imgf); font2=pygame.font.Font(None,t)
    message=''
    pos=pygame.mouse.get_pos()
    pointer=utils.load_image('pointer.png',True)
    pygame.mouse.set_visible(False)
    
    # this activity only
    global board,x0,y0,dd,d2,base,glow,state,border,menu,bgd,top,centre,help1
    global bw,b_img,w_img,smile,frown,green,menu_green,star,star_c,ghost
    global cells # will be pointed to board cells
    board=utils.load_image('board.png',False); s=board.get_width()
    border=sy(.48); s-=2*border
    x0=(w-s)/2; y0=(screen.get_height()-s)/2
    dd=s/8; d2=dd/2; base=.07*float(dd); glow=sy(.27)
    state=0 # will be set in chess.setup()
    # 1:white to move, 2:black to move, 3:black moving, 4:checkmate, 5:stalemate
    # 6:smile, 7:frown
    menu=True
    bgd=utils.load_image('bgd.png',False)
    top=1
    centre=(screen.get_width()/2,screen.get_height()/2)
    help1=False
    bw=None # set in main when buttons setup
    b_img=utils.load_image('black.png',True)
    w_img=utils.load_image('white.png',True)
    smile=utils.load_image('smile.png',True)
    frown=utils.load_image('frown.png',True)
    star=utils.load_image('star.png',True); star_c=[]
    ghost=utils.load_image('ghost.png',True); star_c=[]
    cells=None
    green=None
    menu_green=1
    
def sx(f): # scale x function
    return int(f*factor+offset+.5)

def sy(f): # scale y function
    return int(f*factor+.5)
