from unittest import case
import pygame
import math
from Parabox import *
from Parabox_UI import *

def main():
    #an editor to assemble a level for parabox and export it into compact string
    pygame.init()
    screen = pygame.display.set_mode((1200,800))
    clock = pygame.time.Clock()
    screen.fill((10, 30, 60))
    state="startingMenu"
    data=[]
    DefaultBlocks={"Erase":blocks(),"Wall":wall(),"Block":pushable(),"Patrick":patrick(0),"BGoal":"","PGoal":""}
    AdditionalBlocks={}
    g=game({},None,None)
    oldbox=None
    while not state=="quit":
        blockPalette={**DefaultBlocks,**AdditionalBlocks,**g.boxdict}
        if state=="startingMenu":
            state,g=startingMenu(screen,clock)
            if isinstance(g,game):
                blockPalette={**DefaultBlocks,**AdditionalBlocks,**g.boxdict}
        if state=="gameSpecs":
            state,data=gameSpecs(screen,clock,g)
        elif state=="boxSpecs":
            if not data is None:
                state,data=boxSpecs(screen,clock,g,data)
            else:
                state,data=boxSpecs(screen,clock,g)
            if data in g.boxdict:
                box=g.boxdict[data]
            else:
                box=None
            if isinstance(box,infinity) or isinstance(box,clone):
                data=oldbox
            else:
                oldbox=data
        elif state=="blockSpecs":
            state,data=blockSpecs(screen,clock,g)
        elif state=="levelEditor":
            state,data=levelEditor(screen,clock,g,data,blockPalette)
    pygame.quit()

    return

def startingMenu(screen,clock):
    #the pygame loop for the starting menu
    running=True
    existingLevel=""
    selectionTarget=""
    textEntry=""
    TextEntryMode=False
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return ["quit",None]
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=pygame.mouse.get_pos()
                where=whereStartingMenuClicked(mouseX,mouseY)
                if where=="NewLevel":
                    g=game({},None,None)
                    return ["gameSpecs",g]
                elif where=="ExistingLevel":
                    selectionTarget="ExistingLevel"
                    TextEntryMode=not TextEntryMode
                    textEntry=""
                elif TextEntryMode:
                    TextEntryMode=False
                    existingLevel=textEntry
                    textEntry=""
                    selectionTarget=""
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    return ["quit",None]
                elif event.key==pygame.K_RETURN and TextEntryMode:
                    existingLevel=textEntry
                    textEntry=""
                    TextEntryMode=False
                    selectionTarget=""
                    if existingLevel in Levels:
                        levelString=Levels[existingLevel]
                        g=importGameRLE(levelString)
                        g.Name=existingLevel
                        return ["gameSpecs",g]
                elif event.unicode and TextEntryMode:
                    if event.key==pygame.K_BACKSPACE:
                        textEntry=textEntry[:-1]
                    else:
                        textEntry+=event.unicode
                
                    
        screen.fill((10,30,60))
        draw_StartingMenu(screen,selectionTarget,existingLevel,textEntry,TextEntryMode)
        pygame.display.flip()
        clock.tick(60)
    return

def draw_StartingMenu(screen,selectionTarget,existingLevel:str,textEntry:str,TextEntryMode:bool):
    draw_text(screen,"Patrick's",600,200,200,standardPalette['IntroPat'])
    draw_text(screen,"Editor",600,350,200,standardPalette['IntroPush'])
    draw_text(screen,"By Asymetry",600,450,50,(255,255,255))
    if selectionTarget=="ExistingLevel":
        pygame.draw.rect(screen,(255,255,255),(695,595,210,110),5)
    pygame.draw.rect(screen,(120,240,120),(300,600,200,100))
    draw_text(screen,"New Level",400,650,30,(0,0,0))
    pygame.draw.rect(screen,(150,150,150),(700,600,200,100))
    draw_text(screen,"Existing Level",800,725,30,(255,255,255))
    if TextEntryMode:
        draw_text(screen,textEntry,800,650,min(30,400//(len(textEntry)+1)),(0,0,0))
        if textEntry in Levels:
            pygame.draw.line(screen,(0,255,0),(920,650),(930,665),10)
            pygame.draw.line(screen,(0,255,0),(930,665),(950,635),10)
        else:
            pygame.draw.line(screen,(255,0,0),(920,635),(950,665),10)
            pygame.draw.line(screen,(255,0,0),(950,635),(920,665),10)
    else:
        draw_text(screen,existingLevel,800,650,min(30,400//(len(existingLevel)+1)),(0,0,0))
    return

def whereStartingMenuClicked(mouseX:int,mouseY:int):
    if mouseX>=300 and mouseX<=500 and mouseY>=600 and mouseY<=700:
        return "NewLevel"
    elif mouseX>=700 and mouseX<=900 and mouseY>=600 and mouseY<=700:
        return "ExistingLevel"
    return

def gameSpecs(screen,clock,g):
    #the pygame loop for initializing a game's specs (patrick and wall colors, gamerules, etc)
    running=True
    SelectionTarget=""
    tabs=['SPEC']+list(g.boxdict.keys())
    PalettePage=1
    TextEntryMode=False
    TextEntry=""
    SearchTerm=""
    SearchEntryMode=False
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return ["quit",None]
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=pygame.mouse.get_pos()
                if mouseY<=500:
                    where=whereGameSpecClicked(mouseX,mouseY)
                else:
                    where=whereClickedPalette(mouseX,mouseY,{k:v for k,v in standardPalette.items() if TextEntry.lower() in k.lower()},PalettePage)
                if where=="Name":
                    TextEntryMode=not TextEntryMode
                    TextEntry=""
                    SelectionTarget="Name"
                elif where=="Search" and SelectionTarget in ["Patrick","Pushable"]:
                    SearchEntryMode=not SearchEntryMode
                    TextEntry=""
                elif TextEntryMode and not where =="Name":
                    TextEntryMode=False
                    if SelectionTarget=="Name":
                        g.Name=TextEntry
                    elif SelectionTarget=="Search":
                        SearchTerm=TextEntry
                    TextEntry=""
                    SelectionTarget=""
                elif SearchEntryMode and not where=="Search":
                    SearchEntryMode=False
                    SearchTerm=TextEntry
                    TextEntry=""
                if where=="Patrick" and not SelectionTarget=="Patrick":
                    SelectionTarget="Patrick"
                elif where=="Patrick" and SelectionTarget=="Patrick":
                    SelectionTarget=""
                elif where=="Pushable" and not SelectionTarget=="Pushable":
                    SelectionTarget="Pushable"
                elif where=="Pushable" and SelectionTarget=="Pushable":
                    SelectionTarget=""
                elif where=="NewBox" and g.patCol is not None and g.pushCol is not None:
                    return ["boxSpecs",None]
                elif where=="Default":
                    g.patCol=standardPalette['IntroPat']
                    g.pushCol=standardPalette['IntroPush']
                elif where=="Export" and g.patCol is not None and g.pushCol is not None and g.Name is not None:
                    exportString=g.exportGameRLE()
                    Levels[g.Name]=exportString
                    print("Exported Level:",g.Name)
                    print(exportString)
                    with open("levels.json", "w", encoding="utf-8") as f:
                        json.dump(Levels, f, indent=4)
                    return ["startingMenu",None]
                elif where in standardPalette.keys() and SelectionTarget=="Patrick":
                    g.patCol=standardPalette[where]
                elif where in standardPalette.keys() and SelectionTarget=="Pushable":
                    g.pushCol=standardPalette[where]
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    return ["quit",None]
                if event.key==pygame.K_DOWN and len(tabs)>1:
                    return ["levelEditor",tabs[1]]
                if event.key==pygame.K_LEFT and PalettePage>1 and not SelectionTarget=="":
                    PalettePage-=1
                if event.key==pygame.K_RIGHT and PalettePage*8<len(standardPalette) and not SelectionTarget=="":
                    PalettePage+=1
                elif event.unicode and (TextEntryMode or SearchEntryMode):
                    if event.key==pygame.K_BACKSPACE:
                        TextEntry=TextEntry[:-1]
                    else:
                        TextEntry+=event.unicode
                    if SearchEntryMode:
                        PalettePage=1
        screen.fill((10,30,60))
        draw_GameSpecs(screen,g,SelectionTarget,TextEntry,TextEntryMode)
        if SelectionTarget in ["Patrick","Pushable"] and SearchEntryMode:
            drawPalette(screen,{k:v for k,v in standardPalette.items() if TextEntry.lower() in k.lower()},PalettePage,TextEntry,SearchEntryMode)
        elif SelectionTarget in ["Patrick","Pushable"] and not SearchEntryMode:
            drawPalette(screen,standardPalette,PalettePage,"",False)
        pygame.display.flip()
        clock.tick(60)   
        
    return

def draw_GameSpecs(screen,g:game,highlight:str,TextEntry:str,TextEntryMode:bool):
    #draws the game specs editor onto the screen
    ScreenWidth=screen.get_width()
    ScreenHeight=screen.get_height()
    SpecXstart=100
    SpecYstart=50
    SpecXend=900
    SpecYend=350
    boundsize=200
    boxsize=200*3//4
    patCol=g.patCol
    pushCol=g.pushCol
    if g.patCol is None:
        patCol=(150,150,150)
    if g.pushCol is None:
        pushCol=(150,150,150)
    if highlight=="Patrick":
        pygame.draw.rect(screen,(255,255,255),(SpecXstart-5,SpecYstart-5,boxsize+10,boxsize+10))
    if highlight=="Pushable":
        pygame.draw.rect(screen,(255,255,255),(SpecXstart+boundsize-5,SpecYstart-5,boxsize+10,boxsize+10))
    if highlight=="Name":
        pygame.draw.rect(screen,(255,255,255),(SpecXstart+boundsize*2-5,SpecYstart-5,boxsize+10,boxsize+10))
    pygame.draw.rect(screen,patCol,(SpecXstart,SpecYstart,boxsize,boxsize))
    pygame.draw.rect(screen,pushCol,(SpecXstart+boundsize,SpecYstart,boxsize,boxsize))
    pygame.draw.rect(screen,(150,150,150),(SpecXstart+boundsize*2,SpecYstart,boxsize,boxsize))
    draw_text(screen,"Patrick",SpecXstart+boxsize/2,SpecYstart+boxsize+30,40,(255,255,255))
    draw_text(screen,"Pushable",SpecXstart+boundsize+boxsize/2,SpecYstart+boxsize+30,40,(255,255,255))
    draw_text(screen,"Name",SpecXstart+boundsize*2+boxsize/2,SpecYstart+boxsize+30,40,(255,255,255))
    if not TextEntryMode and not g.Name is None:
        draw_text(screen,g.Name,SpecXstart+boundsize*2+boxsize/2,SpecYstart+boxsize/2,min(40,boxsize*2//(len(g.Name)+1)),(0,0,0))
    if TextEntryMode and highlight=="Name":
        draw_text(screen,TextEntry,SpecXstart+boundsize*2+boxsize/2,SpecYstart+boxsize/2,min(40,boxsize*2//(len(TextEntry)+1)),(0,0,0))
    pygame.draw.rect(screen,(150,150,150),(0,495,1200,10))
    pygame.draw.rect(screen,(120,240,120),(1100,0,100,50))
    pygame.draw.rect(screen,(0,0,0),(1145,10,10,30))
    pygame.draw.rect(screen,(0,0,0),(1135,20,30,10))
    pygame.draw.rect(screen,(100,150,210),(1100,50,100,50))
    draw_text(screen,"Default",1150,75,30,(0,0,0))
    pygame.draw.rect(screen,(250,150,70),(1100,100,100,50))
    draw_text(screen,"Export",1150,125,30,(0,0,0))
    draw_text(screen,"SPEC",1150,250,30,(255,255,255))
    if len(g.boxdict)==0:
        pygame.draw.polygon(screen,(100,100,100),[(1125,275),(1175,275),(1150,300)])
    else:
        pygame.draw.polygon(screen,(150,150,150),[(1125,275),(1175,275),(1150,300)])
    return
    

def whereGameSpecClicked(mouseX:int,mouseY:int):
    #returns what part of the game specs was clicked on
    if mouseX>=100 and mouseX<=250 and mouseY>=50 and mouseY<=200:
        return "Patrick"
    elif mouseX>=300 and mouseX<=450 and mouseY>=50 and mouseY<=200:
        return "Pushable"
    elif mouseX>=500 and mouseX<=650 and mouseY>=50 and mouseY<=200:
        return "Name"
    elif mouseX>=1100 and mouseX<=1200 and mouseY>=0 and mouseY<=50:
        return "NewBox"
    elif mouseX>=1100 and mouseX<=1200 and mouseY>=50 and mouseY<=100:
        return "Default"
    elif mouseX>=1100 and mouseX<=1200 and mouseY>=100 and mouseY<=150:
        return "Export"
    return ""

def boxSpecs(screen,clock,g:game,boxName=""):
    #the pygame loop for initializing a box's specs (dimensions, colors, special properties, etc)
    if boxName in g.boxdict:
        box=g.boxdict[boxName]
        boxRow=box.row
        boxCol=box.col
        boxColor=box.color
        if isinstance(box,infinity):
            boxSpecial="Infinity"
            boxExtension=box.extension.name
        elif isinstance(box,clone):
            boxSpecial="Clone"
            boxExtension=box.extension.name
        elif isinstance(box,epsilon):
            boxSpecial="Epsilon"
            boxExtension=box.extesion.name
        elif isinstance(box,voidbox):
            boxSpecial="Void"
            boxExtension=None
        else:
            boxSpecial=""
            boxExtension=None
    else:
        boxName=""
        boxRow=None
        boxCol=None
        boxColor=None
        boxSpecial=""
        boxExtension=None
    running=True
    TextEntryMode=False
    SearchEntryMode=False
    TextEntry=""
    SelectionTarget=""
    PalettePage=1
    SearchTerm=""
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return ["quit",None]
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=pygame.mouse.get_pos()
                if mouseY<500:
                    where=whereBoxSpecClicked(mouseX,mouseY,boxSpecial)
                elif SelectionTarget=="Color":
                    where=whereClickedPalette(mouseX,mouseY,{k:v for k,v in standardPalette.items() if TextEntry.lower() in k.lower()},PalettePage)
                    if where in standardPalette:
                        boxColor=standardPalette[where]
                    if SearchEntryMode:
                        continue
                elif SelectionTarget=="Extension" and not boxSpecial=="":
                    where=whereClickedPalette(mouseX,mouseY,{k:v for k,v in g.boxdict.items() if TextEntry.lower() in k.lower()},PalettePage)
                    if where in g.boxdict:
                        boxExtension=where
                    if SearchEntryMode:
                        continue
                if TextEntryMode:
                        if SelectionTarget=="Name":
                            boxName=TextEntry
                        elif SelectionTarget=="Row":
                            try:
                                boxRow=int(TextEntry)
                            except:
                                boxRow=None
                        elif SelectionTarget=="Column":
                            try:
                                boxCol=int(TextEntry)
                            except:
                                boxCol=None
                        elif SelectionTarget=="Special" and TextEntry in ["Infinity","Clone","Epsilon","Void"]:
                            boxSpecial=TextEntry
                if where in ["Name","Row","Column","Special"]:
                    TextEntryMode=True
                    TextEntry=""
                    SelectionTarget=where
                    if where=="Name":
                        boxName=""
                    elif where=="Row":
                        boxRow=None
                    elif where=="Column":
                        boxCol=None
                    elif where=="Special":
                        boxSpecial=""
                    continue
                if where=="Search" and SelectionTarget in ["Color","Extension"]:
                    SearchEntryMode=True
                    TextEntryMode=False
                    TextEntry=""
                    continue
                if TextEntryMode:
                    #turn it off if clicking elsewhere
                    TextEntryMode=False
                    TextEntry=""
                    SelectionTarget=""
                if SearchEntryMode:
                    #turn it off if clicking elsewhere
                    SearchEntryMode=False
                    TextEntry=""
                if where=="Color" and SelectionTarget!="Color":
                    PalettePage=1
                    SelectionTarget="Color"
                elif where=="Color" and SelectionTarget=="Color":
                    SelectionTarget=""
                if where=="Extension" and SelectionTarget!="Extension":
                    PalettePage=1
                    SelectionTarget="Extension"
                elif where=="Extension" and SelectionTarget=="Extension":
                    SelectionTarget=""
                if where=="Default":
                    boxName="LR"
                    boxRow=5
                    boxCol=5
                    boxColor=standardPalette["IntroGry"]
                    boxSpecial=""
                    boxExtension=None
                if where=="CreateBox" and not boxName=="" and not boxName in g.boxdict:
                    if boxSpecial=="" and not boxRow is None and not boxCol is None and not boxColor is None:
                        newBox=boxes(boxRow,boxCol,boxName,boxColor)
                    elif boxSpecial=="Infinity" and not boxExtension is None:
                        newBox=infinity(g.boxdict[boxExtension])
                    elif boxSpecial=="Clone" and not boxExtension is None:
                        newBox=clone(g.boxdict[boxExtension])
                    elif boxSpecial=="Epsilon" and not boxExtension is None and not boxRow is None and not boxCol is None:
                        newBox=epsilon(g.boxdict[boxExtension],boxRow,boxCol)
                    elif boxSpecial=="Void":
                        newBox=voidbox(7,7,boxName)
                    else:
                        continue
                    g.boxdict[boxName]=newBox
                    return ["levelEditor",boxName]
                elif where=="CreateBox" and boxName in g.boxdict:
                    box=g.boxdict[boxName]
                    box.color=boxColor
                    return ["levelEditor",boxName]

            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    return ["quit",None]
                elif event.key==pygame.K_RETURN and TextEntryMode:
                    if SelectionTarget=="Name":
                        boxName=TextEntry
                    elif SelectionTarget=="Row":
                        try:
                            boxRow=int(TextEntry)
                        except:
                            boxRow=None
                    elif SelectionTarget=="Column":
                        try:
                            boxCol=int(TextEntry)
                        except:
                            boxCol=None
                    elif SelectionTarget=="Special" and TextEntry in ["Infinity","Clone","Epsilon"]:
                        boxSpecial=TextEntry
                    TextEntryMode=False
                    TextEntry=""
                    SelectionTarget=""
                elif event.unicode and (TextEntryMode or SearchEntryMode):
                    if event.key==pygame.K_BACKSPACE:
                        TextEntry=TextEntry[:-1]
                    else:
                        TextEntry+=event.unicode
                    if SearchEntryMode:
                        PalettePage=1
                elif event.key==pygame.K_LEFT and PalettePage>1 and SelectionTarget=="Color":
                    PalettePage-=1
                elif event.key==pygame.K_RIGHT and PalettePage*8<len(standardPalette) and SelectionTarget=="Color":
                    PalettePage+=1
                #additional key handling for text input would go here
        screen.fill((10,30,60))
        drawBoxSpecs(screen,boxName,boxRow,boxCol,boxColor,boxSpecial,TextEntry,SelectionTarget,TextEntryMode,g,boxExtension)
        if SelectionTarget=="Color":
            drawPalette(screen,{k:v for k,v in standardPalette.items() if TextEntry.lower() in k.lower()},PalettePage,TextEntry,SearchEntryMode)
        elif SelectionTarget=="Extension" and not boxSpecial=="":
            drawPalette(screen,{k:v for k,v in g.boxdict.items() if TextEntry.lower() in k.lower()},PalettePage,TextEntry,SearchEntryMode)
        pygame.display.flip()
        clock.tick(60)

    return

def drawBoxSpecs(screen,boxName:str,boxRow:int,boxCol:int,boxColor:tuple[int,int,int],boxSpecial:str,textEntry,SelectionTarget:str,textEntrymode:bool,g:game,boxExtension:str=None):
    #draws the box specs editor onto the screen
    SpecXstart=100
    SpecYstart=50
    SpecXend=900
    SpecYend=350
    boundsize=200
    boxsize=200*3//4
    descList=["Name","Row","Column","Color","Special"]
    if not boxSpecial=="":
        descList.append("Extension")
    for i in range(6):
        row=i//4
        col=i%4
        if i==5 and boxSpecial in ["","Void"]:
            continue
        if descList[i]==SelectionTarget:
            pygame.draw.rect(screen,(255,255,255),(SpecXstart+boundsize*col-5,SpecYstart+boundsize*row-5,boxsize+10,boxsize+10))
        pygame.draw.rect(screen,(150,150,150),(SpecXstart+boundsize*col,SpecYstart+boundsize*row,boxsize,boxsize))
        draw_text(screen,descList[i],SpecXstart+boundsize*col+boxsize/2,SpecYstart+boundsize*row+boxsize+20,30,(255,255,255))
        if i==0:
            draw_text(screen,boxName,SpecXstart+boundsize*col+boxsize/2,SpecYstart+boundsize*row+boxsize/2,min(40,boxsize*2//(len(boxName)+1)),(0,0,0))
            if boxName in g.boxdict:
                x = SpecXstart + boundsize*col
                y = SpecYstart + boundsize*row
                size = boxsize
                pygame.draw.line(screen,(255,0,0),(x,y),(x+size,y+size),10)
                pygame.draw.line(screen,(255,0,0),(x+size,y),(x,y+size),10)
        elif i==1:
            if boxRow is None:
                boxRow=""
            draw_text(screen,str(boxRow),SpecXstart+boundsize*col+boxsize/2,SpecYstart+boundsize*row+boxsize/2,min(40,boxsize*2//(len(str(boxRow))+1)),(0,0,0))
            if boxSpecial in ["Infinity","Clone","Void"] or boxName in g.boxdict:
                x = SpecXstart + boundsize*col
                y = SpecYstart + boundsize*row
                size = boxsize
                pygame.draw.line(screen,(255,0,0),(x,y),(x+size,y+size),10)
                pygame.draw.line(screen,(255,0,0),(x+size,y),(x,y+size),10)
        elif i==2:
            if boxCol is None:
                boxCol=""
            draw_text(screen,str(boxCol),SpecXstart+boundsize*col+boxsize/2,SpecYstart+boundsize*row+boxsize/2,min(40,boxsize*2//(len(str(boxCol))+1)),(0,0,0))
            if boxSpecial in ["Infinity","Clone","Void"] or boxName in g.boxdict:
                x = SpecXstart + boundsize*col
                y = SpecYstart + boundsize*row
                size = boxsize
                pygame.draw.line(screen,(255,0,0),(x,y),(x+size,y+size),10)
                pygame.draw.line(screen,(255,0,0),(x+size,y),(x,y+size),10)
        elif i==3:
            if boxColor is None:
                pygame.draw.rect(screen,(150,150,150),(SpecXstart+boundsize*col,SpecYstart+boundsize*row,boxsize,boxsize))
            else:
                pygame.draw.rect(screen,boxColor,(SpecXstart+boundsize*col,SpecYstart+boundsize*row,boxsize,boxsize))
            if boxSpecial in ["Infinity","Clone","Void","Epsilon"]:
                x = SpecXstart + boundsize*col
                y = SpecYstart + boundsize*row
                size = boxsize
                pygame.draw.line(screen,(255,0,0),(x,y),(x+size,y+size),10)
                pygame.draw.line(screen,(255,0,0),(x+size,y),(x,y+size),10)
        elif i==4:
            draw_text(screen,boxSpecial,SpecXstart+boundsize*col+boxsize/2,SpecYstart+boundsize*row+boxsize/2,min(40,boxsize*2//(len(boxSpecial)+1)),(0,0,0))
            if boxName in g.boxdict:
                x = SpecXstart + boundsize*col
                y = SpecYstart + boundsize*row
                size = boxsize
                pygame.draw.line(screen,(255,0,0),(x,y),(x+size,y+size),10)
                pygame.draw.line(screen,(255,0,0),(x+size,y),(x,y+size),10)
        if descList[i]==SelectionTarget and textEntrymode:
            draw_text(screen,textEntry,SpecXstart+boundsize*col+boxsize/2,SpecYstart+boundsize*row+boxsize/2,min(40,boxsize*2//(len(textEntry)+1)),(0,0,0))
        elif i==5 and boxExtension is not None:
            draw_boxes(screen,SpecXstart+boundsize*col,SpecYstart+boundsize*row,boxsize,g.boxdict[boxExtension].color,boxExtension[1:])
            if boxName in g.boxdict:
                x = SpecXstart + boundsize*col
                y = SpecYstart + boundsize*row
                size = boxsize
                pygame.draw.line(screen,(255,0,0),(x,y),(x+size,y+size),10)
                pygame.draw.line(screen,(255,0,0),(x+size,y),(x,y+size),10)

        
    pygame.draw.rect(screen,(150,150,150),(0,495,1200,10))
    pygame.draw.rect(screen,(120,240,120),(1100,0,100,50))
    pygame.draw.line(screen,(0,0,0),(1135,25),(1145,35),10)
    pygame.draw.line(screen,(0,0,0),(1145,35),(1165,15),10)
    pygame.draw.rect(screen,(100,150,210),(1100,50,100,50))
    draw_text(screen,"Default",1150,75,30,(0,0,0))
    
    return

def whereBoxSpecClicked(mouseX:int,mouseY:int,boxSpecial:str):
    #returns what part of the box specs was clicked on
    descList=["Name","Row","Column","Color","Special"]
    if not boxSpecial=="":
        descList.append("Extension")
    for i in range(6):
        row=i//4
        col=i%4
        if i==5 and boxSpecial=="":
            continue
        rectx=100+200*col
        recty=50+200*row
        if mouseX>=rectx and mouseX<=rectx+150 and mouseY>=recty and mouseY<=recty+150 and i in range(5):
            return descList[i]
        elif mouseX>=rectx and mouseX<=rectx+150 and mouseY>=recty and mouseY<=recty+150 and i==5 and not boxSpecial=="":
            return descList[5]
    if mouseX>=1100 and mouseX<=1200 and mouseY>=0 and mouseY<=50:
        return "CreateBox"
    if mouseX>=1100 and mouseX<=1200 and mouseY>=50 and mouseY<=100:
        return "Default"
    return ""

def blockSpecs():
    #not implemented yet, but for initializing a block's specs (play order, possession, etc)

    return

def levelEditor(screen,clock,g:game,boxname:str,blockPalette:dict):
    #the pygame loop for the level editor itself
    box:Union[boxes,pseudoboxes]=g.boxdict[boxname]
    running=True
    PalettePage=1
    Selection1=[None,None]
    Selection2=[None,None]
    RectMode=False
    if isinstance(box,voidbox):
        color=(0,0,0)
    elif isinstance(box,epsilon):
        color=box.extension.color
    else:
        color=box.color
    while running:
        BoxTabs=filter(lambda x: isinstance(g.boxdict[x],boxes) or isinstance(g.boxdict[x],epsilon),list(g.boxdict))
        BoxDict={k:g.boxdict[k] for k in BoxTabs}
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return ["quit",None]
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouseX,mouseY=pygame.mouse.get_pos()
                if mouseY<=500:
                    where=whereLevelEditorClicked(mouseX,mouseY,g,box)
                else:
                    where=whereClickedPalette(mouseX,mouseY,blockPalette,PalettePage)
                if isinstance(where,tuple):
                    if not RectMode and not Selection1==list(where):
                        Selection1=list(where)
                    elif not RectMode and Selection1==list(where):
                        Selection1=[None,None]
                    elif RectMode and Selection1==[None,None]:
                        Selection1=list(where)
                    elif RectMode and not Selection1==[None,None] and Selection2==[None,None]:
                        Selection2=list(where)
                    elif RectMode and not Selection1==[None,None] and not Selection2==[None,None]:
                        Selection1=list(where)
                        Selection2=[None,None]
                if where =="Delete":
                    Index=g.boxdict.pop(boxname)
                    if Index>1:
                        newKey=list(g.boxdict.keys())[Index-1]
                        return ["levelEditor",newKey]
                    return ["gameSpecs",None]
                if where=="Border":
                    Selection1=[None,None]
                    Selection2=[None,None]
                    box.fillborder(wall())
                if where=="BoxSpecs":
                    return ["boxSpecs",boxname]
                if where in blockPalette.keys() and not Selection1==[None,None]:
                    #place block(s) logic
                    if not RectMode or Selection2==[None,None]:
                        row=Selection1[0]
                        col=Selection1[1]
                        if isinstance(blockPalette[where],boxes) or isinstance(blockPalette[where],epsilon):
                            box.place(row,col,blockPalette[where])
                        elif where in ["BGoal","PGoal"]:
                            box.placeGoal(row,col,where[0].lower())
                        elif where=="Erase":
                            box.place(row,col,blocks())
                            if [row,col] in box.bgoals:
                                box.bgoals.remove([row,col])
                            if [row,col] in box.pgoals:
                                box.pgoals.remove([row,col])
                        else:
                            box.place(row,col,copy.deepcopy(blockPalette[where]))
                    elif RectMode:
                        minRow=min(Selection1[0],Selection2[0])
                        maxRow=max(Selection1[0],Selection2[0])
                        minCol=min(Selection1[1],Selection2[1])
                        maxCol=max(Selection1[1],Selection2[1])
                        if isinstance(blockPalette[where],boxes) or isinstance(blockPalette[where],epsilon):
                            box.fillrect(minRow,minCol,maxRow,maxCol,blockPalette[where])
                        else:
                            box.fillrect(minRow,minCol,maxRow,maxCol,copy.deepcopy(blockPalette[where]))
                    Selection1=[None,None]
                    Selection2=[None,None]
                    PalettePage=1
                if where=="Add":
                    Selection1=[None,None]
                    Selection2=[None,None]
                    return ["boxSpecs",None]
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    return ["quit",None]
                elif event.key==pygame.K_LEFT and PalettePage>1:
                    PalettePage-=1
                elif event.key==pygame.K_RIGHT and PalettePage*8<len(blockPalette):
                    PalettePage+=1
                elif event.key==pygame.K_r:
                    RectMode=not RectMode
                elif event.key==pygame.K_UP:
                    pos=list(BoxDict).index(boxname)
                    if pos>0:
                        newKey=list(BoxDict.keys())[pos-1]
                        return ["levelEditor",newKey]
                    return ["gameSpecs",None]
                elif event.key==pygame.K_DOWN:
                    pos=list(BoxDict).index(boxname)
                    if pos+1<len(BoxDict):
                        newKey=list(BoxDict.keys())[pos+1]
                        return ["levelEditor",newKey]
        screen.fill((10,30,60))
        drawLevelEditor(screen,g,box,Selection1,Selection2,RectMode)
        if not Selection1==[None,None]:
            drawPalette(screen,blockPalette,PalettePage,boxColor=color,g=g)
        pygame.display.flip()
        clock.tick(60)
    return

def drawLevelEditor(screen,g:game,box:Union[boxes,pseudoboxes],Selection1:list,Selection2:list,RectMode:bool):
    #draws the level editor onto the screen
    boundingSize=400
    cellsize=boundingSize/box.row
    drawBoard(screen,400,50,cellsize,box,g)
    for i in range(box.row+1):
        pygame.draw.line(screen,(0,0,0),(400,50+i*cellsize),(400+boundingSize,50+i*cellsize),2)
        pygame.draw.line(screen,(0,0,0),(400+i*cellsize,50),(400+i*cellsize,50+boundingSize),2)
    if not Selection1==[None,None]:
        pygame.draw.line(screen,(255,255,255),(400+Selection1[1]*cellsize,50+Selection1[0]*cellsize),(400+(Selection1[1]+1)*cellsize,50+Selection1[0]*cellsize),4)
        pygame.draw.line(screen,(255,255,255),(400+Selection1[1]*cellsize,50+Selection1[0]*cellsize),(400+Selection1[1]*cellsize,50+(Selection1[0]+1)*cellsize),4)
        pygame.draw.line(screen,(255,255,255),(400+(Selection1[1]+1)*cellsize,50+Selection1[0]*cellsize),(400+(Selection1[1]+1)*cellsize,50+(Selection1[0]+1)*cellsize),4)
        pygame.draw.line(screen,(255,255,255),(400+Selection1[1]*cellsize,50+(Selection1[0]+1)*cellsize),(400+(Selection1[1]+1)*cellsize,50+(Selection1[0]+1)*cellsize),4)
    if not Selection2==[None,None] and RectMode:
        #rectmode logic
        pygame.draw.line(screen,(255,255,255),(400+Selection2[1]*cellsize,50+Selection2[0]*cellsize),(400+(Selection2[1]+1)*cellsize,50+Selection2[0]*cellsize),4)
        pygame.draw.line(screen,(255,255,255),(400+Selection2[1]*cellsize,50+Selection2[0]*cellsize),(400+Selection2[1]*cellsize,50+(Selection2[0]+1)*cellsize),4)
        pygame.draw.line(screen,(255,255,255),(400+(Selection2[1]+1)*cellsize,50+Selection2[0]*cellsize),(400+(Selection2[1]+1)*cellsize,50+(Selection2[0]+1)*cellsize),4)
        pygame.draw.line(screen,(255,255,255),(400+Selection2[1]*cellsize,50+(Selection2[0]+1)*cellsize),(400+(Selection2[1]+1)*cellsize,50+(Selection2[0]+1)*cellsize),4)
        minRow=min(Selection1[0],Selection2[0])
        maxRow=max(Selection1[0]+1,Selection2[0]+1)
        minCol=min(Selection1[1],Selection2[1])
        maxCol=max(Selection1[1]+1,Selection2[1]+1)
        pygame.draw.line(screen,(255,255,255),(400+minCol*cellsize,50+minRow*cellsize),(400+maxCol*cellsize,50+minRow*cellsize),2)
        pygame.draw.line(screen,(255,255,255),(400+minCol*cellsize,50+minRow*cellsize),(400+minCol*cellsize,50+maxRow*cellsize),2)
        pygame.draw.line(screen,(255,255,255),(400+maxCol*cellsize,50+minRow*cellsize),(400+maxCol*cellsize,50+maxRow*cellsize),2)
        pygame.draw.line(screen,(255,255,255),(400+minCol*cellsize,50+maxRow*cellsize),(400+maxCol*cellsize,50+maxRow*cellsize),2)
    pygame.draw.rect(screen,(120,240,120),(1100,0,100,50))
    pygame.draw.rect(screen,(0,0,0),(1145,10,10,30))
    pygame.draw.rect(screen,(0,0,0),(1135,20,30,10))
    pygame.draw.rect(screen,(255,0,0),(1100,50,100,50))
    draw_text(screen,"Delete",1150,75,30,(0,0,0))
    pygame.draw.rect(screen,(100,150,210),(0,0,100,50))
    if RectMode:
        draw_text(screen,"R",50,25,30,(255,255,255))
    else:
        draw_text(screen,"R",50,25,30,(0,0,0))
    if isinstance(box,boxes):
        pygame.draw.rect(screen,tuple(c*0.6 for c in box.color),(0,50,100,50))
        draw_bgoals(screen,25,50,50,box.color)
    else:
        pygame.draw.rect(screen,tuple(c*0.6 for c in box.extension.color),(0,50,100,50))
        draw_bgoals(screen,25,50,50,box.extension.color)
    
    draw_text(screen,box.name,1150,250,30,(255,255,255))
    pygame.draw.polygon(screen,(150,150,150),[(1125,225),(1175,225),(1150,200)])
    pos=list(g.boxdict).index(box.name)
    if pos+1>=len(g.boxdict):
        pygame.draw.polygon(screen,(100,100,100),[(1125,275),(1175,275),(1150,300)])
    else:
        pygame.draw.polygon(screen,(150,150,150),[(1125,275),(1175,275),(1150,300)])
    return

def whereLevelEditorClicked(mouseX:int,mouseY:int,g:game,box:Union[boxes,pseudoboxes]):
    boundingSize=400
    cellsize=boundingSize/box.row
    if mouseX>=400 and mouseX<=800 and mouseY>=50 and mouseY<=450:
        col=int((mouseX-400)/cellsize)
        row=int((mouseY-50)/cellsize)
        return (row,col)
    if mouseX>=1100 and mouseX<=1200 and mouseY>=0 and mouseY<=50:
        return "Add"
    if mouseX>=0 and mouseX<=100 and mouseY>=50 and mouseY<=100:
        return "Border"
    if mouseX>=1100 and mouseX<=1200 and mouseY>=225 and mouseY<=275:
        return "BoxSpecs"
    return

def drawPalette(screen,paletteDict:dict,page:int,textEntry:str="",searchEntryMode:bool=False,boxColor=None,g:game=None):
    #draws from a palette of items onto the screen for selection
    #six items per page
    paletteList=list(paletteDict.keys())
    pageNeeded=math.ceil(len(paletteList)/8)
    if pageNeeded==0:
        draw_text(screen,"0/"+str(pageNeeded),600,550,30,(255,255,255))
    else:
        draw_text(screen,str(page)+"/"+str(pageNeeded),600,550,30,(255,255,255))
    pygame.draw.polygon(screen,(255,255,255),[(580,545),(570,550),(580,555)])
    pygame.draw.polygon(screen,(255,255,255),[(620,545),(630,550),(620,555)])
    for i in range(8):
        bound=1000
        boxsize=80
        Segstart=100
        boundsize=125
        rectx=Segstart+i*boundsize+boundsize/2-boxsize/2
        recty=600

        if i+8*(page-1)>=len(paletteList):
            pygame.draw.rect(screen,(100,100,100),(rectx,recty,80,80))
            continue
        itemName=paletteList[i+8*(page-1)]
        item=paletteDict[itemName]
        if isinstance(item,tuple):
            pygame.draw.rect(screen,item,(rectx,recty,80,80))
            draw_text(screen,itemName,rectx+40,recty+90,min(20,boxsize*2//(len(itemName)+1)),(255,255,255))
        elif itemName=="BGoal":
            draw_bgoals(screen,rectx,recty,80,boxColor)
            draw_text(screen,"BGoal",rectx+40,recty+90,20,(0,0,0))
        elif itemName=="PGoal":
            draw_pgoals(screen,rectx,recty,80,boxColor)
            draw_text(screen,"PGoal",rectx+40,recty+90,20,(0,0,0))
        elif not item.tangible:
            draw_tile(screen,rectx,recty,80,boxColor)
            draw_text(screen,"Erase",rectx+40,recty+90,20,(0,0,0))
        elif isinstance(item,wall):
            draw_wall(screen,rectx,recty,80,boxColor)
            draw_text(screen,"Wall",rectx+40,recty+90,20,(0,0,0))
        elif isinstance(item,pushable):
            draw_pushable(screen,rectx,recty,80,g.pushCol)
            draw_text(screen,"Pushable",rectx+40,recty+90,20,(0,0,0))
        elif isinstance(item,patrick):
            draw_patrick(screen,rectx,recty,80,g.patCol,item.order)
            draw_text(screen,"Patrick"+str(item.order),rectx+40,recty+90,20,(0,0,0))
           
        elif isinstance(item,boxes):
            draw_boxes(screen,rectx,recty,80,tuple(min(255,int(1.2*c)) for c in item.color),item.name.removeprefix('L'))
            draw_text(screen,item.name.removeprefix('L'),rectx+40,recty+90,min(20,boxsize*2//(len(item.name))),(0,0,0))
        elif isinstance(item,infinity):
            draw_boxes(screen,rectx,recty,80,tuple(min(255,int(0.75*c)) for c in item.extension.color),"INF-"+item.extension.name[1:])
            draw_text(screen,"INF-"+item.extension.name.removeprefix('L'),rectx+40,recty+90,min(20,boxsize*2//(len("INF-"+item.extension.name)+1)),(0,0,0))
        elif isinstance(item,clone):
            draw_boxes(screen,rectx,recty,80,tuple(min(255,int(1.8*c)) for c in item.extension.color),item.extension.name[1:])
            draw_text(screen,"CLN-"+item.extension.name.removeprefix('L'),rectx+40,recty+90,min(20,boxsize*2//(len("CLN-"+item.extension.name))),(0,0,0)) 
        else:
            pygame.draw.rect(screen,(100,100,100),(rectx,recty,80,80))
        
    if searchEntryMode:
        pygame.draw.rect(screen,(255,255,255),(895,520,210,60))
        pygame.draw.rect(screen,(150,150,150),(900,525,200,50))  
        draw_text(screen,textEntry,1000,550,30,(0,0,0))
    else:
        pygame.draw.rect(screen,(150,150,150),(900,525,200,50))       
    return

def whereClickedPalette(mouseposX:int,mouseposY:int,paletteDict:dict,page:int):
    #returns the name of the item clicked on in the palette
    for i in range(8):
        bound=1000
        boxsize=80
        Segstart=100
        boundsize=125
        rectx=Segstart+i*boundsize+boundsize/2-boxsize/2
        recty=600
        if mouseposX>=rectx and mouseposX<=rectx+boxsize and mouseposY>=recty and mouseposY<=recty+boxsize:
            if i+8*(page-1)>=len(paletteDict):
                return ""
            itemName=list(paletteDict.keys())[i+8*(page-1)]
            return itemName
        if mouseposX>=900 and mouseposX<=1100 and mouseposY>=525 and mouseposY<=575:
            return "Search"
    return

if __name__ == "__main__":
    main()
