import pygame
from Parabox import *
import math
pygame.font.init()
_font_cache = {}



def get_font(size=20):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont(None, size)
    return _font_cache[size]

def draw_text(screen, text, x, y, size=20, color=(255,255,255), center=True):
    font = get_font(size)
    surf = font.render(str(text), True, color)
    if center:
        rect = surf.get_rect(center=(x, y))
        screen.blit(surf, rect)
    else:
        screen.blit(surf, (x, y))
def drawBoard(screen,startX,startY,cellsize,box:boxes,g:game):
    for i in range(0,box.col):
        for j in range(0,box.row):
            tile=box.board[j][i]
            tileX=startX+i*cellsize
            tileY=startY+j*cellsize
            if not tile.tangible:
                if isinstance(box,voidbox):
                    pygame.draw.rect(screen,(0,0,0),(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize)))
                    continue
                draw_tile(screen,tileX,tileY,cellsize,box.color)
                if [j,i] in box.bgoals:
                    draw_bgoals(screen,tileX,tileY,cellsize,box.color)
                elif [j,i] in box.pgoals:
                    draw_pgoals(screen,tileX,tileY,cellsize,box.color)
            elif isinstance(tile,wall):
                draw_wall(screen,tileX,tileY,cellsize,box.color)
            elif isinstance(tile,pushable):
                draw_pushable(screen,tileX,tileY,cellsize,g.pushCol)
                if [j,i] in box.bgoals:
                    draw_aura(screen,tileX,tileY,cellsize,(255,255,255))

            elif isinstance(tile,patrick):
                draw_patrick(screen,tileX,tileY,cellsize,g.patCol,tile.order)
                if [j,i] in box.pgoals:
                    draw_aura(screen,tileX,tileY,cellsize,(255,255,255))
            elif isinstance(tile,boxes):
                draw_boxes(screen,tileX,tileY,cellsize,tuple(min(255,int(1.05*c)) for c in tile.color),tile.name[1:])
                if [j,i] in box.bgoals:
                    draw_aura(screen,tileX,tileY,cellsize,(255,255,255))
                if isinstance(tile.container,voidbox):
                    draw_aura(screen,tileX,tileY,cellsize,(250,250,130))
            elif isinstance(tile,infinity):
                draw_boxes(screen,tileX,tileY,cellsize,tuple(min(255,int(0.75*c)) for c in tile.extension.color),"INF-"+tile.extension.name[1:])
                draw_aura(screen,tileX,tileY,cellsize,(250,250,130))
                if [j,i] in box.bgoals:
                    draw_aura(screen,tileX,tileY,cellsize,(255,255,255))
            if isinstance(tile,clone):
                draw_boxes(screen,tileX,tileY,cellsize,tuple(min(255,int(1.25*c)) for c in tile.extension.color),tile.extension.name[1:])
                if [j,i] in box.bgoals:
                    draw_aura(screen,tileX,tileY,cellsize,(255,255,255))
                    
            
                    
def drawGame(screen,g:game):
    numRow,numCol=optimalGrid(len(g.boxdict),screen.get_width()/screen.get_height())
    shareX=screen.get_width()/numCol
    shareY=screen.get_height()/numRow
    biggestSquare=min(shareX,shareY)
    for i in range(len(g.boxdict)):
        row=i//numCol
        col=i%numCol
        box=list(g.boxdict.values())[i]
        if isinstance(box,clone) or isinstance(box,infinity):
            continue
        centerX,centerY=(shareX*col+shareX/2,shareY*row+shareY/2)
        cornerX,cornerY=centerX-biggestSquare/2,centerY-biggestSquare/2
        startX,startY=cornerX+biggestSquare/8,cornerY+biggestSquare/8
        cellsize=(biggestSquare*3/4)/max(box.row,box.col)
        drawBoard(screen,startX,startY,cellsize,box,g)
        if isinstance(box,voidbox):
            draw_text(screen,"VOID",math.ceil(cornerX+biggestSquare/8),math.ceil(cornerY+biggestSquare/16),math.ceil(biggestSquare/10),(255,255,255))
            continue
        draw_text(screen,box.name[1:],math.ceil(cornerX+biggestSquare/16),math.ceil(cornerY+biggestSquare/16),math.ceil(biggestSquare/10),(255,255,255))
#okay since it seems like I am gonna have to reuse drawing code for tiles
#Im gonna separate these out into functions

def draw_tile(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,boxcolor:tuple[int,int,int]):
    pygame.draw.rect(screen,tuple(min(255,int(c*0.75)) for c in boxcolor),(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize)))

def draw_bgoals(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,boxcolor:tuple[int,int,int]):
    pygame.draw.rect(screen,tuple(min(255,int(c*1.25)) for c in boxcolor),(math.ceil(tileX+cellsize/8),math.ceil(tileY+cellsize/8),math.ceil(cellsize*3/4),math.ceil(cellsize*3/4)))
    pygame.draw.rect(screen,tuple(min(255,int(c*0.75)) for c in boxcolor),(math.ceil(tileX+cellsize/4),math.ceil(tileY+cellsize/4),math.ceil(cellsize/2),math.ceil(cellsize/2)))

def draw_pgoals(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,boxcolor:tuple[int,int,int]):
    pygame.draw.rect(screen,tuple(min(255,int(c*1.25)) for c in boxcolor),(math.ceil(tileX+cellsize/8),math.ceil(tileY+cellsize/8),math.ceil(cellsize*3/4),math.ceil(cellsize*3/4)))
    pygame.draw.circle(screen,tuple(min(255,int(c*0.75)) for c in boxcolor),(math.ceil(tileX+cellsize*5/16),math.ceil(tileY+cellsize*5/16)),math.ceil(cellsize/12))
    pygame.draw.circle(screen,tuple(min(255,int(c*0.75)) for c in boxcolor),(math.ceil(tileX+cellsize*11/16),math.ceil(tileY+cellsize*5/16)),math.ceil(cellsize/12))

def draw_wall(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,boxcolor:tuple[int,int,int]):
    pygame.draw.rect(screen,boxcolor,(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize)))

def draw_pushable(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,pushcolor:tuple[int,int,int]):
    pygame.draw.rect(screen,pushcolor,(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize)))

def draw_aura(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,color:tuple[int,int,int]):
    pygame.draw.rect(screen,color,(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize/16)))
    pygame.draw.rect(screen,color,(math.ceil(tileX),math.ceil(tileY+cellsize*15/16),math.ceil(cellsize),math.ceil(cellsize/16)))
    pygame.draw.rect(screen,color,(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize/16),math.ceil(cellsize)))
    pygame.draw.rect(screen,color,(math.ceil(tileX+cellsize*15/16),math.ceil(tileY),math.ceil(cellsize/16),math.ceil(cellsize)))

def draw_patrick(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,patcolor:tuple[int,int,int],order:int):
    pygame.draw.rect(screen,patcolor,(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize)))
    draw_text(screen,"P"+str(order),math.ceil(tileX+cellsize/2),math.ceil(tileY+cellsize/2),math.ceil(cellsize/2),(0,0,0))
                
def draw_boxes(screen:pygame.Surface,tileX:float,tileY:float,cellsize:float,color:tuple[int,int,int],name:str):
    pygame.draw.rect(screen,color,(math.ceil(tileX),math.ceil(tileY),math.ceil(cellsize),math.ceil(cellsize)))
    draw_text(screen,name,math.ceil(tileX+cellsize/2),math.ceil(tileY+cellsize/2),math.ceil(min(cellsize/2,cellsize*1.5/len(name)+1)),(0,0,0))



def optimalGrid(numboxes,aspectRatio):
    rows=1
    cols=1
    while rows*cols<numboxes:
        rowPlus=(cols/(rows+1))
        colPlus=((cols+1)/rows)
        if abs(rowPlus-aspectRatio)<abs(colPlus-aspectRatio):
            rows+=1
        else:
            cols+=1
    return rows,cols

def LevelPartition(Levels):
    Chapters=['Intro','Enter','Empty','Eat','Reference','Swap','Center']
    #returns a dict of chapters with a list of levels ordered by number
    ChapterLevels={}
    for chapter in Chapters:
        ChapterLevels[chapter]=filter(lambda lvl: lvl.startswith(chapter), Levels.keys())
        ChapterLevels[chapter]=sorted(ChapterLevels[chapter],key=lambda x: int(x[len(chapter):]))
    return ChapterLevels
def Chapterselect(screen,clock):
    Chapters=['Intro','Enter','Empty','Eat','Reference','Swap','Center']
    page=1
    running=True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ['quit',None]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ['quit',None]
                elif event.key == pygame.K_RIGHT and page<math.ceil(len(Chapters)/12):
                    page+=1
                elif event.key == pygame.K_LEFT and page>1:
                    page-=1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=pygame.mouse.get_pos()
                #determine if a level was clicked
                #if so, return that level's game object
                #else continue
                chapterClicked=WhereClicked(mouseX,mouseY,Chapters,page)
                if chapterClicked is not None:
                    return ['Level',chapterClicked]
        #draw
        screen.fill((10, 30, 60))
        draw_level_select(screen,Chapters,"Chapter Select",page)
        pygame.display.flip()
        clock.tick(60)

def Levelselect(screen,clock,chapter):   
    ChapterLevels=LevelPartition(Levels)[chapter]
    running=True
    page=1
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ['Chapter',None]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ['Chapter',None]
                elif event.key == pygame.K_RIGHT and page<math.ceil(len(ChapterLevels)/12):
                    page+=1
                elif event.key == pygame.K_LEFT and page>1:
                    page-=1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=pygame.mouse.get_pos()
                #determine if a level was clicked
                #if so, return that level's game object
                #else continue
                LevelClicked=WhereClicked(mouseX,mouseY,ChapterLevels,page)
                if LevelClicked is not None:
                    return ['Game',importGameRLE(Levels[LevelClicked])]
        #draw
        screen.fill((10, 30, 60))
        draw_level_select(screen,ChapterLevels,chapter,page)
        pygame.display.flip()
        clock.tick(60)
    

def draw_level_select(screen,list,title,page):
    #used for both chapter and level select
    pagesNeeded=math.ceil(len(list)/12)
    draw_text(screen,title,screen.get_width()//2,50,40,(255,255,255))
    draw_text(screen,"Page "+str(page)+" of "+str(pagesNeeded),screen.get_width()//2,100,30,(200,200,200))
    for i in range(1,13):
        row=(i-1)//4
        col=(i-1)%4
        boxWidth=screen.get_width()/6
        if i-1+12*(page-1)>=len(list):
            pygame.draw.rect(screen,(100,100,100),(math.ceil(col*boxWidth+225),math.ceil(row*boxWidth+150),math.ceil(boxWidth*3/4),math.ceil(boxWidth*3/4)))
            continue
        if list[i-1+12*(page-1)].startswith(title):
            text=list[i-1+12*(page-1)].removeprefix(title)
        else:
            text=list[i-1+12*(page-1)]
        pygame.draw.rect(screen,(150,150,150),(math.ceil(col*boxWidth+225),math.ceil(row*boxWidth+150),math.ceil(boxWidth*3/4),math.ceil(boxWidth*3/4)))
        draw_text(screen,text,math.ceil(col*boxWidth+225+boxWidth*3/8),math.ceil(row*boxWidth+150+boxWidth*3/8),30,(0,0,0))
    return
    #used for both chapter and level select
    

def WhereClicked(mouseX,mouseY,list,page):
    #returns the level or chapter clicked on, or None if none clicked
    pageNeeded=math.ceil(len(list)/12)
    if mouseY<150 or mouseY>150+math.ceil(200*(2.75)):
        return None
    if mouseX<225 or mouseX>225+math.ceil(200*(3.75)):
        return None
    #out of bounds, no need for further checks
    for i in range(1,13):
        row=(i-1)//4
        col=(i-1)%4
        boxXStart=math.ceil(col*200+225)
        boxYStart=math.ceil(row*200+150)
        boxXEnd=math.ceil(col*200+225+200*3/4)
        boxYEnd=math.ceil(row*200+150+200*3/4)
        if mouseX>=boxXStart and mouseX<=boxXEnd and mouseY>=boxYStart and mouseY<=boxYEnd:
            index=i-1+12*(page-1)
            if index>=len(list):
                return None
            return list[index]

def main():
    pygame.init()
    screen = pygame.display.set_mode((1200,800))
    clock = pygame.time.Clock()
    screen.fill((10, 30, 60))
    
    #screen control
    state='Chapter'
    data=[]
    levelSelected=None
    while not state=='quit':
        if state=='Chapter':
            Output=Chapterselect(screen,clock)
            if Output[0]=='Level':
                levelSelected=Output[1]
        if state=='Level':
            Output=Levelselect(screen,clock,levelSelected)
            if Output[0]=='Game':
                gameString=Output[1]
        if state=='Game':
            Output=RunGame(screen,clock,gameString)
        state=Output[0]

        
    pygame.quit()
def RunGame(screen,clock,g,inEditor=False):
    running = True
    while running:
        # ---- input ----
        # check win state at top of loop so input can be ignored when won
        game_won = False
        try:
            game_won = g.checkWin() 
        except Exception:
            # if g or g.box isn't available yet, treat as not-won
            game_won = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ['Level',None]
            elif event.type == pygame.KEYDOWN:
                # ignore movement keys if game already won
                if event.key == pygame.K_ESCAPE:
                    return ['Level',None]
                if game_won:
                    # swallow movement keys after win
                    continue
                if event.key == pygame.K_UP:
                    g.move(0)
                elif event.key == pygame.K_DOWN:
                    g.move(2)
                elif event.key == pygame.K_LEFT:
                    g.move(1)
                elif event.key == pygame.K_RIGHT:
                    g.move(3)
                elif event.key == pygame.K_r:
                    g=g.reset()
                elif event.key == pygame.K_z:
                    g.undo()
                elif event.key == pygame.K_x:
                    g.redo()
                
            # handle other events here (keyboard, mouse...)

        # ---- update ----
        # (game updates)

        # ---- draw ----
        # clear screen each frame so changes (moves) are visible
        screen.fill((10, 30, 60))
        drawGame(screen,g)

        # if the game is won, draw a semi-transparent overlay and message
        if game_won:
            try:
                overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                draw_text(screen, "You Win!", screen.get_width()//2, screen.get_height()//2 - 20, size=48, color=(255,255,255))
                draw_text(screen, "Press ESC or close window to exit", screen.get_width()//2, screen.get_height()//2 + 30, size=20, color=(200,200,200))
            except Exception:
                # fall back to simple text if overlay fails
                draw_text(screen, "You Win!", screen.get_width()//2, screen.get_height()//2, size=48, color=(255,255,255))
        pygame.display.flip()  
        clock.tick(60)  # limit FPS

if __name__ == "__main__":
    main()


