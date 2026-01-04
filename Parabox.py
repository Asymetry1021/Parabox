from __future__ import annotations
import copy
from itertools import combinations
from typing import Union
import json

with open("levels.json", "r", encoding="utf-8") as f:
    Levels = json.load(f)

standardPalette={
    #grays
    'IntroGry':(225,225,225),
    'EnterGry':(150,180,220),
    'EmptyGry':(200,190,190),
    'CentGry':(130,130,160),
    #blues
    'IntroBlu':(50,150,250),
    'EatBlu':(100,130,230),
    'RefBlu':(30,140,170),
    #yellows
    'IntroYel':(250,190,60),
    'EnterYel':(210,250,50),
    'EatYel':(250,220,130),
    'RefYel':(220,190,60),
    'ClnYel':(220,210,0),
    #pinks
    'IntroPat':(200,10,120),
    'EnterPat':(200,60,120), 
    'EatPat':(210,110,200),
    'RefPnk':(250,50,100),
    #greens
    'EnterGrn':(50,250,150),
    'EnterLim':(90,250,50),
    'EmptyGrn':(180,210,60),
    'EatGrn':(120,240,120),
    'CentGrn':(110, 160, 50),
    'ClnGrn':(120,210,40),
    #oranges
    'EnterOrg':(230,140,70), 
    'EmptyPat':(225,90,40),
    'EatOrg':(250,180,130),
    'RefPat':(180,50,60),
    #purples
    'RefPur':(140,100,250), 
    'CentPat':(130,70,220),
    }

with open('standardPalette.json','w') as f:
    json.dump(standardPalette,f,indent=4)


class blocks:
    #the general class for any block of any nature
    tangible=False
    pushable=False
    playable=False
    def __init__(self):
        #this specifically is used for empty blocks, the default block
        self.container=None
        self.rootrow=None
        self.rootcol=None
        return

class boxes(blocks):
    #has a defined interior and dimensions, also boolean
    pushable=True
    tangible=True
    def __init__(self,row:int,col:int,name:str=None,color:tuple[int,int,int]=(50,150,250)):
        super().__init__()
        self.row=row
        self.col=col
        self.name=name
        self.board=[[blocks() for j in range(col)] for i in range(row)]
        for i in range(0,row):
            for j in range(0,col):
                self.board[i][j].container=self
                self.board[i][j].outrow=i
                self.board[i][j].outcol=j
        #creates a box of dimension rowxcol of emptys
        self.bgoals=[]
        self.pgoals=[]
        if isinstance(color,str):
            self.color=standardPalette[color]
        else:
            self.color=color #default color is none, which means greyscale

    def place(self,row:int,col:int,block:blocks):
        if 0<=row<self.row and 0<=col<self.col:
            self.board[row][col]=block
            block.container=self
            block.rootrow=row
            block.rootcol=col
        else:
            print("error: out of bounds")
    
    def placeGoal(self,row:int,col:int,goaltype:str):
        if [row,col] in self.bgoals or [row,col] in self.pgoals:
            print("error: goal already exists")
            return
        if goaltype=='b':
            self.bgoals.append([row,col])
        elif goaltype=='p':
            self.pgoals.append([row,col])
        else:
            print("error: invalid goal type")
    
    def printbox(self):
        #also doubles as a way to find all the children boxes
        children=[]
        for i in range(self.row):
            rep=[]
            for j in range(self.col):
                space=self.board[i][j]
                if type(space) is blocks:
                    if [i,j] in self.bgoals:
                       rep.append('B')
                    elif [i,j] in self.pgoals:
                       rep.append('P')
                    else:
                       rep.append('_')
                elif type(space) is boxes:
                    rep.append(space.name[1:])
                    children.append(space)
                elif type(space) is wall:
                    rep.append('#')
                elif type(space) is pushable:
                    rep.append('+')
                elif type(space) is patrick:
                    rep.append('p')
            print(''.join(rep))
        return children
    
    def checkGoals(self):
        #checks if all goals are met
        for goal in self.bgoals:
            row,col=goal
            if type(self.board[row][col]) is not pushable and type(self.board[row][col]) is not boxes:
                return False
        for goal in self.pgoals:
            row,col=goal
            if type(self.board[row][col]) is not patrick:
                return False
        return True
    
    def exportBox(self):
        exportstr=self.name
        children=[] #a list of sub-boxes in the box to be compressed separately
        exportstr+=":"+str(self.row)+","+str(self.col)+","+str(self.color[0])+","+str(self.color[1])+","+str(self.color[2])
        for i in range(self.row):
            for j in range(self.col):
                space=self.board[i][j]
                if type(space) is wall:
                    exportstr+=":#,"+str(i)+","+str(j)
                elif type(space) is pushable:
                    exportstr+=":+,"+str(i)+","+str(j)
                elif type(space) is patrick:
                    exportstr+=":p"+str(space.order)+","+str(i)+","+str(j)
                elif type(space) is boxes or type(space) is voidbox:
                    exportstr+=":"+space.name+","+str(i)+","+str(j)
                    children.append(space)
                elif type(space) is infinity:
                    exportstr+=":"+space.name+","+str(i)+","+str(j)
                if [i,j] in self.bgoals:
                    exportstr+=":B,"+str(i)+","+str(j)
                if [i,j] in self.pgoals:
                    exportstr+=":P,"+str(i)+","+str(j)
        return exportstr
    
    def exportBoxRLE(self):
        #a new version of export box that uses RLE compression
        Specs=self.name+";"+str(self.row)+","+str(self.col)+";"+str(self.color[0])+","+str(self.color[1])+","+str(self.color[2])
        if isinstance(self,voidbox):
            Specs+=";V"
        #Specs complete for now
        boardstr=exportBoardRLE(self.board)
        goalstr=exportGoalsRLE(self.bgoals,self.pgoals)
        exportstr=Specs+':'+boardstr
        if goalstr!="":
            exportstr+=':'+goalstr[:-1]
        return exportstr   
                        
                    

    #Helper functions for making boxes easier
    def fillrow(self,row:int,blocktype:blocks):
        for j in range(self.col):
            self.place(row,j,blocktype)
    
    def fillcol(self,col:int,blocktype:blocks):
        for i in range(self.row):
            self.place(i,col,blocktype)
    
    def fillrect(self,startrow:int,startcol:int,endrow:int,endcol:int,blocktype:blocks):
        for i in range(startrow,endrow+1):
            for j in range(startcol,endcol+1):
                self.place(i,j,blocktype)
    
    def fillborder(self,blocktype:blocks):
        self.fillrow(0,blocktype)
        self.fillrow(self.row-1,blocktype)
        self.fillcol(0,blocktype)
        self.fillcol(self.col-1,blocktype)

def exportBoardRLE(board):
    #Isolated lookup and RLEboard export into its own function as epsilons are pseudoboxes with interior
    #So I can deferr the export for epsilons to have a BoardRLE
    Lookup=""
    LookupDict={}
    LookupIndex=0
    boardstr=""
    row=len(board)
    col=len(board[0])
    streakBlock=board[0][0]
    streakCount=0
    for i in range(row):
        for j in range(col):
            tile=board[i][j]
            if equivalent(tile,streakBlock):
                streakCount+=1
            else:
                #flush streak
                if not any(equivalent(lookups,streakBlock) for lookups in LookupDict.values()):
                    LookupDict[LookupIndex]=streakBlock
                    if not streakBlock.tangible:
                        Lookup+=str(LookupIndex)+',_;'
                    elif type(streakBlock) is wall:
                        Lookup+=str(LookupIndex)+',#;'
                    elif type(streakBlock) is pushable:
                        Lookup+=str(LookupIndex)+',+;'
                    elif type(streakBlock) is patrick:
                        Lookup+=str(LookupIndex)+',p'+str(streakBlock.order)+';'
                    elif isinstance(streakBlock,boxes) or isinstance(streakBlock,pseudoboxes):
                        Lookup+=str(LookupIndex)+','+streakBlock.name+';'
                    LookupIndex+=1
                for key in LookupDict:
                    if equivalent(LookupDict[key],streakBlock):
                        BlockID=key
                        break
                boardstr+=str(BlockID)+','+str(streakCount)+';'
                streakBlock=tile
                streakCount=1
                BlockID=None
    #flush last streak
    if not any(equivalent(lookups,streakBlock) for lookups in LookupDict.values()):
        [LookupIndex]=streakBlock
        if not streakBlock.tangible:
            Lookup+=str(LookupIndex)+',_;'
        elif type(streakBlock) is wall:
            Lookup+=str(LookupIndex)+',#;'
        elif type(streakBlock) is pushable:
            Lookup+=str(LookupIndex)+',+;'
        elif type(streakBlock) is patrick:
            Lookup+=str(LookupIndex)+',p'+str(streakBlock.order)+';'
        elif type(streakBlock) is boxes or type(streakBlock) is voidbox or type(streakBlock) is pseudoboxes:
            Lookup+=str(LookupIndex)+','+streakBlock.name+';'
    for key in LookupDict:
        if equivalent(LookupDict[key],streakBlock):
            BlockID=key
            break
    boardstr+=str(BlockID)+','+str(streakCount)+';'  
    return Lookup[:-1]+':'+boardstr[:-1]


def exportGoalsRLE(bgoals,pgoals):
    goalstr=""
    for goal in bgoals:
        goalstr+='B,'+str(goal[0])+','+str(goal[1])+';' 
    for goal in pgoals:
        goalstr+='P,'+str(goal[0])+','+str(goal[1])+';'
    return goalstr


class wall(blocks):
    tangible=True


class pushable(blocks):
    tangible=True
    pushable=True

class patrick(blocks):
    tangible=True
    pushable=True
    playable=True
    def __init__(self,order:int):
        super().__init__()
        # ensure instance-level flags are set so they are not accidentally shadowed
        self.tangible = True
        self.pushable = True
        self.playable = True
        self.order=order

    tangible=False

class voidbox(boxes):
    #void boxes are boxes where nothing can enter into boxes within them. They have black backgrounds.
    def __init__(self,row:int,col:int,name:str=None):
        super().__init__(row,col,name)
        self.color=(0,0,0) #void boxes are always black
class pseudoboxes(blocks):
    tangible=True
    pushable=True
    playable=False
    def __init__(self,truebox:Union[boxes,pseudoboxes]):
        super().__init__()
        self.extension=truebox
    
    def exportPseudoRLE(self):
        #a new version of export box that uses RLE compression
        Specs=self.name
        if isinstance(self,infinity):
            Specs+=";I,"+self.extension.name+","+str(self.tier)
        if isinstance(self,clone):
            Specs+=";C,"+self.extension.name
        #Specs complete for now
        #once flips and epsilons which have interiers are added, the board copy will be needed
        return Specs
        

class infinity(pseudoboxes):
    #infinity boxes can not be entered period
    def __init__(self,truebox:Union[boxes,pseudoboxes]):
        super().__init__(truebox)
        if truebox is None:
            self.name=""
        else:
            self.name='I'+truebox.name
        self.tier=1 #initially set as tier 1. 
        #When infinite exit comes around eventually there will be tiers of infinity and epsilons
    
    def generateVoid(self):
        #generates a void box containing nothing but itself
        void=voidbox(7,7,'V'+self.name)
        void.place(3,3,self)
    
class clone(pseudoboxes):
    #clones reference the interior of another box for entering only
    def __init__(self,truebox:Union[boxes,pseudoboxes]):
        super().__init__(truebox)
        if not truebox is None:
            self.name='C'+truebox.name

class epsilon(pseudoboxes):
    #the paradox breaker for infinite enters
    def __init__(self,truebox:Union[boxes,pseudoboxes],row=5,col=5):
        super().__init(truebox)
        self.row=row
        self.col=col
        self.board=[[blocks() for j in range(col)] for i in range(row)]
        for i in range(0,row):
            for j in range(0,col):
                self.board[i][j].container=self
                self.board[i][j].outrow=i
                self.board[i][j].outcol=j
        #creates a box of dimension rowxcol of emptys
        self.bgoals=[]
        self.pgoals=[]
    #as epsilons have an interior, it has all the usual suspects of helper placer functions
    def place(self,row:int,col:int,block:blocks):
        if 0<=row<self.row and 0<=col<self.col:
            self.board[row][col]=block
            block.container=self
            block.rootrow=row
            block.rootcol=col
        else:
            print("error: out of bounds")
    
    def placeGoal(self,row:int,col:int,goaltype:str):
        if [row,col] in self.bgoals or [row,col] in self.pgoals:
            print("error: goal already exists")
            return
        if goaltype=='b':
            self.bgoals.append([row,col])
        elif goaltype=='p':
            self.pgoals.append([row,col])
        else:
            print("error: invalid goal type")

    def fillrow(self,row:int,blocktype:blocks):
        for j in range(self.col):
            self.place(row,j,blocktype)
    
    def fillcol(self,col:int,blocktype:blocks):
        for i in range(self.row):
            self.place(i,col,blocktype)
    
    def fillrect(self,startrow:int,startcol:int,endrow:int,endcol:int,blocktype:blocks):
        for i in range(startrow,endrow+1):
            for j in range(startcol,endcol+1):
                self.place(i,j,blocktype)
    
    def fillborder(self,blocktype:blocks):
        self.fillrow(0,blocktype)
        self.fillrow(self.row-1,blocktype)
        self.fillcol(0,blocktype)
        self.fillcol(self.col-1,blocktype)

    def generateVoid(self):
        #generates a void box containing nothing but itself
        void=voidbox(7,7,'V'+self.name)
        void.place(3,3,self)
    
    def exportPseudoRLE(self):
        Specs=super().exportPseudoRLE()
        boardstr=exportBoardRLE(self.board)
        goalstr=exportGoalsRLE(self.bgoals,self.pgoals)
        exportstr=Specs+':'+boardstr
        if goalstr!="":
            exportstr+=':'+goalstr[:-1]
        return exportstr 


class game:
    #uses a boxdict instead of a rootbox to generate a game
    def __init__(self,boxdict:dict,patcol:tuple[int,int,int]=(200,10,120),pushcol:tuple[int,int,int]=(250,210,20)):
        self.playerlist=[]
        self.undochain=[]
        self.redochain=[]
        self.boxdict=boxdict
        self.Name=None #only used for level storage
        searchedboxes=set()
        for box in boxdict.values():
            if isinstance(box,infinity) or isinstance(box,clone):
                continue
            for i in range(box.row):
                for j in range(box.col):
                    block=box.board[i][j]
                    if isinstance(block,patrick) and block not in self.playerlist:
                        self.playerlist.append(block)
        self.playerlist.sort(key=lambda x: x.order)
        self.initial=""
        if isinstance(patcol,str) and isinstance(pushcol,str):
            self.patCol=standardPalette[patcol]
            self.pushCol=standardPalette[pushcol]
        else:
            self.patCol=patcol
            self.pushCol=pushcol
    
    def printGame(self):
        printedboxes=[]
        for box in list(self.boxdict.values()):
            if isinstance(box,infinity) or isinstance(box,clone):
                continue
            print(box.name)
            box.printbox()
        #defunct soon as we have proper UI, keep this for the time being but will delete later
        #will have more functions later on with nested boxes
    
    def move(self,direction:int):
        #0,1,2,3 N,W,S,E
        #moves every player block
        self.undochain.append(self.exportGameRLE())
        self.redochain=[]
        for player in self.playerlist:
            push(player.container,player.rootrow,player.rootcol,direction,[],self)
        self.checkWin()
        self.printGame()
    
    def checkWin(self):
        for boxes in self.boxdict.values():
            if not boxes.checkGoals():
                return False
        return True
    
    def undo(self):
        if len(self.undochain)>0:
            self.redochain.append(self.exportGameRLE())
            previousstate=importGameRLE(self.undochain.pop())
            self.boxdict=previousstate.boxdict
            self.playerlist=previousstate.playerlist
            self.printGame()
        else:
            print("No more undos available")
    
    def redo(self):
        if len(self.redochain)>0:
            self.undochain.append(self.exportGameRLE())
            nextstate=importGameRLE(self.redochain.pop())
            self.boxdict=nextstate.boxdict
            self.playerlist=nextstate.playerlist
            self.printGame()
        else:
            print("No more redos available")
    
    def reset(self):
        return importGameRLE(self.initial)
    
    def setcolor(self,name:str,color:Union[str,tuple[int,int,int]]):
        if name=='Pat':
            self.patCol=standardPalette[color]
        elif name=='Push':
            self.pushCol=standardPalette[color]
        elif name in self.boxdict:
            #if a box is not in the game, assigning a color will do nothing
            self.boxdict[name].color=standardPalette[color]
        
    def exportGame(self):
        #exports the game into a compact string format for easy sharing
        #for phase 1, only need to export the root box
        #for phase 2, same deal as import, need to compress every sub-box as they show up
        #will be deleted once all current levels have been converted to the new format
        gamecode= ""
        queue=list(reversed(list(self.boxdict.values())))
        while queue:
            currentbox=queue.pop(0)
            boxstring=currentbox.exportBox()
            gamecode+=boxstring+'|'
        gamecode=gamecode[:-1] #removes the last |
        return gamecode
    def exportGameRLE(self):
        #a new version of export game that uses RLE compression
        #step 1: spec generation
        gamecode="SPEC:"+str(self.patCol[0])+","+str(self.patCol[1])+","+str(self.patCol[2])+":"+str(self.pushCol[0])+","+str(self.pushCol[1])+","+str(self.pushCol[2])+'|'
        queue=list(self.boxdict.values())
        cloneChecker=[]
        while queue:
            currentbox=queue.pop(0)
            if isinstance(currentbox,pseudoboxes):
                if isinstance(currentbox,clone):
                    if currentbox.extension.name in cloneChecker:
                        continue
                    #saves only the first(original) clone of each box
                    boxstring=currentbox.exportPseudoRLE()
                    cloneChecker.append(currentbox.extension.name)
                if isinstance(currentbox,infinity):
                    boxstring=currentbox.exportPseudoRLE()
            else:
                boxstring=currentbox.exportBoxRLE()
            gamecode+=boxstring+'|'
        return gamecode[:-1] #removes the last |

        


#functions go here


        

def push(box,row,col,direction,pushlist,game):
        #cycle checker
        if len(pushlist)>1:
            lastbox=pushlist[-1]
            for i in range(len(pushlist)-1):
                if pushlist[i]==lastbox:
                    cyclelist=pushlist[i+1:]
                    firstbox,firstrow,firstcol=cyclelist[0].container,cyclelist[0].rootrow,cyclelist[0].rootcol
                    for j in range(len(cyclelist)-1):
                        nextbox,nextrow,nextcol=cyclelist[j+1].container,cyclelist[j+1].rootrow,cyclelist[j+1].rootcol
                        nextbox.place(nextrow,nextcol,cyclelist[j])
                    firstbox.place(firstrow,firstcol,cyclelist[-1])
                    return 2 #special return signal, indicates a cycle has occured and nothing else (entry, eat, etc) should take place
        #if no cycle occurs, regular pushing continues
        #pushes/moves
        #maybe returns a 0 or 1 to determine if the push is successful and recursively pass the signal up?
        delx,dely=0,0
        if direction%2==0:
            dely=direction-1
        else:
            delx=direction-2
        #pushing out
        if row+dely not in range(0,box.row) or col+delx not in range(0,box.col):
            success=exitOut(box.board[row][col],box.container,box.rootrow,box.rootcol,direction,[box],pushlist,game)
            if success==1:
                box.board[row][col]=blocks()
                return 1
            if success==2:
                return 2 #cycle detected, stop further actions
            else:
                return 0
   
        nextblock=box.board[row+dely][col+delx] #gets the block in its direction
        if not nextblock.tangible:
            box.place(row+dely,col+delx,box.board[row][col]) #move itself to the empty spot
            box.board[row][col]=blocks() #replaces the space behind it with an empty
            return 1 #signals that the move was successful for next layers
        elif not nextblock.pushable:
            return 0 #the next block is a wall, nothing happens
        else:
            #if nextblock is both tangible and pushable i.e a block, box, or another player
            pushlist.append(nextblock)
            success=push(box,row+dely,col+delx,direction,pushlist,game) #check if the block in front can push/move
            if success==1:
                box.board[row+dely][col+delx]=box.board[row][col] 
                box.board[row][col]=blocks() 
                box.board[row+dely][col+delx].rootrow=row+dely
                box.board[row+dely][col+delx].rootcol=col+delx 
                return 1
            if success==2:
                return 2 #cycle detected, stop further actions
            if isinstance(nextblock,boxes):
                #pushing/entering into a box
                success=enterIn(box.board[row][col],nextblock,direction,[],pushlist,game) #enter and exit will also give 0,1 inputs
                if success==1:
                    box.board[row][col]=blocks()
                    return 1
                
            if isinstance(box.board[row][col],boxes):
                #eat
                success=enterIn(box.board[row+dely][col+delx],box.board[row][col],(direction+2)%4,[],[],game)
                if success==1:
                    box.place(row+dely,col+delx,box.board[row][col])
                    box.board[row][col]=blocks()
                    return 1
                else:
                    return 0

                #actually hold on scratch all of this
                #multi-exit and enters are needed, we need to define it rigorously and hopefully as independent recursive functions instead of as push
                #enter and exit functions
            else:
                return 0

def accessible(box,direction):
    #checks if a box can be accessed from a direction
    entdict={2:[0,box.col//2],3:[box.row//2,0],0:[box.row-1,box.col//2],1:[box.row//2,box.col-1]}
    entrow,entcol=entdict[direction]
    targetblock=box.board[entrow][entcol]
    if not targetblock.tangible:
        return True
    elif not targetblock.pushable:
        return False
    else:
        if isinstance(targetblock,boxes):
            return accessible(targetblock,direction)
        else:
            return False
    #if the block blocking the entrance is empty or a pushable, it will attempt to enter the box (and push if needed)

def equivalent(a,b):
    #checks if two block objects are close enough to be considered equivalent
    if isinstance(a,clone) and isinstance(b,clone) and a.extension.name==b.extension.name:
        return True
    if isinstance(a,wall) and isinstance(b,wall):
        return True
    if isinstance(a,pushable) and isinstance(b,pushable):
        return True
    if not(a.tangible) and not(b.tangible):
        return True
    if isinstance(a,patrick) and isinstance(b,patrick) and a.order==b.order:
        return True
    if (isinstance(a,boxes) or isinstance(a,pseudoboxes)) and (isinstance(b,boxes) or isinstance(b,pseudoboxes)) and a.name==b.name:
        return True
    return False

def importGame(gamecode):
    #imports a game from a compact string format
    boxstringdict= {}
    installdict={}#a dictionary for each box to denote where and which sub-box is to be properly installed
    initializedboxes={}# a dict of box names with box objects that are defined(but not nessecarily filled with sub-boxes yet)
    specs=gamecode.split('|')[0]
    if specs.startswith("SPEC:"):
        speclist=specs[5:].split(':')
        #currently no specs are defined, but in the future patrick colors, pushable colors, and so on can be defined here
        patCol=tuple(map(int,speclist[0].split(',')))
        pushCol=tuple(map(int,speclist[1].split(',')))
        gamecode=gamecode.split('|')[1:]
    else:
        patCol=(200,10,120)
        pushCol=(250,210,20)
    for box in gamecode.split("|"):
        name,rest=box.split(":",1)
        boxstringdict[name]=rest
    while len(boxstringdict)>0:
        currentboxname,currentboxcode=boxstringdict.popitem() #get the next box to be implemented
        if currentboxname in initializedboxes:
            continue
        currentbox,children=importBox(currentboxname+':' + currentboxcode)
        installdict[currentboxname]=children
        initializedboxes[currentboxname]=currentbox
    #all the needed boxes are initialized, now to implement the nesting
    for boxname in installdict:
        orders=installdict[boxname]
        for order in orders:
            name,row,col=order
            if name[0]=='I':
                #infinity box (not yet initialized)
                trueboxname=name[1:]
                truebox=initializedboxes[trueboxname]
                infbox=infinity(truebox)
                initializedboxes[name]=infbox #adds the psuedobox to the initialized boxes for future reference
                initializedboxes[boxname].place(row,col,infbox)
                #later on, multiple infinites would make this a bit more complicated. 
                #Idk if Im going with the chains of infinities or tier idea
                #but this will get more complex a lot later on
            elif name[0]=='C':
                #clone box (not yet initialized)
                trueboxname=name[1:]
                truebox=initializedboxes[trueboxname]
                clbox=clone(truebox)
                initializedboxes[boxname].place(row,col,clbox)
            else:
                initializedboxes[boxname].place(row,col,initializedboxes[name])
    g=game(initializedboxes)
    g.initial=gamecode
    g.patCol=patCol
    g.pushCol=pushCol
    return g

def importBox(boxcode):
    #ok might be easier to split it up into individual boxes. Reference list of boxes already made?
    #instead of outputting the rootbox maybe it just outputs the dictionary of all boxes implemented?
    #what even is the structure of game?
    #ok maybe game has a lookup table of boxes by name?
    #on second thought a lookup table might not be such a good idea. just do the rootbox and have the rootbox carry everything.
    #might be concerning when we add infinity and epsilons but we will get there when we get there
    parts=boxcode.split(":",2)
    if len(parts)<3:
        title,dims=parts
        rest=''
    else:
        title,dims,rest=parts
    implementNesting=[] # a nested array containing all the data needed for box implementation
    specifics=dims.split(",")
    if len(specifics)==2:
        row,col=map(int,specifics)
        color=(50,150,250) #default color
    else:
        row,col,r,g,b=map(int,specifics)
        color=(r,g,b)
    if title[0]=='V':
        rootBox=voidbox(row,col,title)
    else:
        rootBox=boxes(row,col,name=title)
        rootBox.color=color
    alterations=rest.split(":")
    for alt in alterations:
        if alt=='':
            continue
        bType,row,col=alt.split(",",2)
        row=int(row)
        col=int(col)
        if bType=='#':
            rootBox.place(row,col,wall())
        elif bType=='+':
            rootBox.place(row,col,pushable())
        elif bType[0]=='p':
            order=int(bType[1:])
            rootBox.place(row,col,patrick(order))
        elif bType[0]=='I':
            #infinity box
            #note: truebox would have not yet been set up, so the creation of infinity must be deferred to after all boxes are created
            implementNesting.append([bType,row,col])
        elif bType[0]=='C':
            #clone box
            #note: truebox would have not yet been set up, so the creation of clone must be deferred to after all boxes are created
            implementNesting.append([bType,row,col])
        elif bType=='B':
            rootBox.placeGoal(row,col,'b')
        elif bType=='P':
            rootBox.placeGoal(row,col,'p')
        elif bType[0]=='L':
            #the alteration is another box in the string
            implementNesting.append([bType,row,col])
            #for now, the spaces where the block would be is empty, will be implemented all at once at importGame
    return [rootBox,implementNesting]

def importGameRLE(gamecode):
    #a new version of import game that uses the RLE method
    boxecodes=gamecode.split("|")
    specs=boxecodes[0]
    pColstr,puColstr=specs[5:].split(":",1)
    patCol=tuple(map(int,pColstr.split(',')))
    pushCol=tuple(map(int,puColstr.split(',')))
    initializedboxes={}
    installdict={}
    for boxcode in boxecodes[1:]:
        box,orders=importBoxRLE(boxcode)
        installdict[box.name]=orders
        initializedboxes[box.name]=box
    #all boxes initialized, now to implement nesting and other connections
    cloneIDs={}
    for boxname in installdict:
        orders=installdict[boxname]
        if isinstance(initializedboxes[boxname],infinity) or isinstance(initializedboxes[boxname],clone):
            #psuedoboxes which have one singular order
            initializedboxes[boxname].extension=initializedboxes[orders[0]]
    for boxname in installdict:
        orders=installdict[boxname]
        if isinstance(initializedboxes[boxname],infinity) or isinstance(initializedboxes[boxname],clone):
            continue
        for order in orders:
            name,row,col=order
            if isinstance(initializedboxes[name],clone):
                if name not in cloneIDs:
                    cloneIDs[name]=0
                    initializedboxes[boxname].place(row,col,initializedboxes[name])
                else:
                    cloneIDs[name]+=1
                    newClone=copy.deepcopy(initializedboxes[name])
                    newCloneName=name+str(cloneIDs[name])
                    initializedboxes[newCloneName]=newClone
            initializedboxes[boxname].place(row,col,initializedboxes[name])
    g=game(initializedboxes,patCol,pushCol)
    g.initial=gamecode
    return g

def importBoxRLE(boxcode):
    #a new version of import box that uses the RLE method
    parts=boxcode.split(":")
    orders=[]
    if len(parts)==1:
        specs=parts[0]
        lookupstr=""
        boardstr=""
        goalstr=""
    elif len(parts)==3:
        specs,lookupstr,boardstr=parts
        goalstr=""
    else:
        specs,lookupstr,boardstr,goalstr=parts
    #specs parsing
    specslist=specs.split(";")
    name=specslist[0]
    for specs in specslist[1:]:
        desclist=specs.split(",")
        if desclist[0]=='I':
            box=infinity(None)
            box.tier=int(desclist[2])
            box.name='I'+desclist[1]
            order=desclist[1]
            return box,[order]
        if desclist[0]=='C':
            box=clone(None)
            box.name='C'+desclist[1]
            order=desclist[1]
            return box,[order]
        #the interiorless pseudoboxes just needs to have their extensions assiged when they are initialized
    row,col=map(int,specslist[1].split(","))
    r,g,b=map(int,specslist[2].split(","))
    color=(r,g,b)
    if 'V' in specslist:
        box=voidbox(row,col,name)
    else:
        box=boxes(row,col,name)
        box.color=color
    #lookup parsing
    if lookupstr=="":
        lookupentries=[]
    else:
        lookupentries=lookupstr.split(";")
    lookupdict={}
    for entry in lookupentries:
        idcode,blockcode=entry.split(",",1)
        idcode=int(idcode)
        if blockcode=='_':
            lookupdict[idcode]=blocks()
        elif blockcode=='#':
            lookupdict[idcode]=wall()
        elif blockcode=='+':
            lookupdict[idcode]=pushable()
        elif blockcode[0]=='p':
            order=int(blockcode[1:])
            lookupdict[idcode]=patrick(order)
        else:
            #box or pseudobox
            lookupdict[idcode]=blockcode
    #board parsing
    if boardstr=="":
        boardentries=[]
    else:
        boardentries=boardstr.split(";")
    boardRLElist=[]
    for entry in boardentries:
        idcode,count=entry.split(",",1)
        idcode=int(idcode)
        count=int(count)
        boardRLElist.append([idcode,count])
    #goal parsing
    if goalstr=="":
        goalentries=[]
    else:
        goalentries=goalstr.split(";")
    for entry in goalentries:
        goaltype,row,col=entry.split(",",2)
        row=int(row)
        col=int(col)
        if goaltype=='B':
            box.placeGoal(row,col,'b')
        elif goaltype=='P':
            box.placeGoal(row,col,'p')
    #assembly of board from RLE
    blockID,blockLeft=boardRLElist.pop(0)
    for i in range(box.row):
        for j in range(box.col):
            block=lookupdict[blockID]
            if isinstance(block,str):
                #box or pseudobox not yet initialized
                orders.append([block,i,j])                
            else:
                box.place(i,j,copy.deepcopy(block))
            blockLeft-=1
            if blockLeft==0 and len(boardRLElist)>0:
                blockID,blockLeft=boardRLElist.pop(0)
    return box,orders



def enterIn(block,box,direction,inlist,pushlist,game):
    #block is trying to enter a box in direction
    if isinstance(box,infinity):
        return 0 #infinity boxes can not be entered
    if isinstance(block.container,voidbox):
        return 0 #blocks inside void boxes can not enter other boxes
    if isinstance(box,clone):
        box=box.extension #clones redirect to their true box for entering
    entdict={2:[0,box.col//2],3:[box.row//2,0],0:[box.row-1,box.col//2],1:[box.row//2,box.col-1]}
    if box.name in inlist:
        #infinite enter detected
        epsbox=epsilon(block.container)
        epsbox.generateVoid()
        game.boxdict[epsbox.container.name]=epsbox.container #the first repeated box generates an infinity box in a void. To ensure stuff like A-B-C-C-C... loops at C
        game.boxdict[epsbox.name]=epsbox
        return enterIn(block,epsbox,direction,inlist,pushlist,game)   
    entrow,entcol=entdict[direction]
    targetblock=box.board[entrow][entcol]
    if not targetblock.tangible:
        box.place(entrow,entcol,block)
        return 1
    elif not targetblock.pushable:
        return 0
    else:
        pushlist.append(targetblock)
        success=push(box,entrow,entcol,direction,pushlist,game) #push the block infront the entrance in the direction
        if success==1:
            box.place(entrow,entcol,block)
            return 1
        elif isinstance(targetblock,boxes):
            inlist.append(targetblock.name)
            return enterIn(block,targetblock,direction,inlist,pushlist,game) #enter and exit will also give 0,1 inputs in addition to entering the block
        else:
            return 0

def exitOut(block,box,row,col,direction,outlist,pushlist,game):
    #lets do this one first
    #block is trying to exit a box(positioned at row, col in Box) in direction
    #this attempts an exit out of container boxes until a space is found, then attempts to either move/push to that space
    if box is None:
        return 0 #no space exist outside the root box
    deldict={0:[-1,0],1:[0,-1],2:[1,0],3:[0,1]}
    dely,delx=deldict[direction]
    if isinstance(block.container,voidbox):
        return 0 #void boxes can not be exited from
    if box.name in outlist:
        #infinite exit detected
        infbox=infinity(block.container)
        infbox.generateVoid()
        game.boxdict[infbox.container.name]=infbox.container #the first repeated box generates an infinity box in a void. To ensure stuff like A-B-C-C-C... loops at C
        game.boxdict[infbox.name]=infbox
        return exitOut(block,infbox.container,3,3,direction,outlist,pushlist,game)
    targetrow,targetcol=row+dely,col+delx
    if targetrow not in range(0,box.row) or targetcol not in range(0,box.col):
        outlist.append(box.name)
        success=exitOut(block,box.container,box.rootrow,box.rootcol,direction,outlist,pushlist,game)
        if success==1:
            return 1
        else:
            return 0
    targetblock=box.board[targetrow][targetcol]
    if not targetblock.tangible:
        box.place(targetrow,targetcol,block)
        return 1
    elif not targetblock.pushable:
        return 0
    else:
        pushlist.append(targetblock)
        success=push(box,targetrow,targetcol,direction,pushlist,game) #orders the targetblock to attempt a move/push in the direction
        if success==1:
            box.place(targetrow,targetcol,block)
            return 1
        if success==2:
            return 2 #cycle detected, stop further actions
        if isinstance(block,boxes):
            #exiting a box by eating the obstruction
            success=enterIn(block,box.container,(direction+2)%4,[],[],game)
            if success==1:
                block.container.place(block.rootrow,block.rootcol,blocks())
                box.place(targetrow,targetcol,block)
                return 1
            else:
                return 0
        else:
            return 0

def convert(oldcode):
    #converts old game code to new game code
    g=importGame(oldcode)
    return g.exportGameRLE()

def PaletteConvert(GameList, BoxList, Palette):
    #given a list of generic box/attribute names, assigns a color to each of them based on the palette for all game codes in game list
    ConvertedGames=map(lambda x:importGameRLE(x),GameList)
    Output=[]
    for game in ConvertedGames:
        for i in range(0,len(BoxList)):
            game.setcolor(BoxList[i],Palette[i])
        Output.append(game.exportGameRLE())
    return Output
        
def nearestColor(color:tuple[int,int,int]):
    #given an rgb color, returns the name of the nearest standard palette color
    minDist=99999
    nearestName=None
    for name in standardPalette:
        stdColor=standardPalette[name]
        dist=(color[0]-stdColor[0])**2+(color[1]-stdColor[1])**2+(color[2]-stdColor[2])**2
        if dist<minDist:
            minDist=dist
            nearestName=name
    if minDist>625:
        print("No close color found. Nearest color is " + nearestName+":"+str(standardPalette[nearestName])+", with distance "+str(minDist))
    else:
        print("Matching color is " + nearestName+":"+str(standardPalette[nearestName])+", with distance "+str(minDist))

def crossReference():
    #detects which pair of palettes are too close
    combs=list(combinations(standardPalette.values(), 2))
    for comb in combs:
        colorA,colorB=comb
        dist=(colorA[0]-colorB[0])**2+(colorA[1]-colorB[1])**2+(colorA[2]-colorB[2])**2
        if dist<1000:
            nameA=None
            nameB=None
            for name in standardPalette:
                if standardPalette[name]==colorA:
                    nameA=name
                if standardPalette[name]==colorB:
                    nameB=name
            print("Colors "+nameA+" and "+nameB+" are too close, with distance "+str(dist))
    
Intro=[['LR','LA'],['IntroGry','IntroBlu']]
#block types: pNumber=patric, +=push, #=wall

#goals
#new idea: instead of making them a block like default empty spaces, make them a property of boxes themselves. 
#Have them only display when printing if the block on them is the default empty block

#Box Encoding:
#Boxes will be given names from imports, and automatically generates names if not given for exports
#ok for future notice
#encoding box names can prob store more meaning
#like LCLname or LRFname or LINFname can be used to denote clones, reflections, and infinity variants of box Lname

#added root boxes, rootrow, and rootcol to give each box context of where it is in the parent box
#place now automatically sets those values when placing a box inside another box

#with boxdict, I don't think root boxes are a needed concept anymore. 
#With stuff like swap and clone, having a root box is no longer a useful concept.
#Need to rework game, import/export, and everything that involved root boxes to make use of boxdict instead
#ok for printing I dont really want the boxes to be in random order. I guess we could do it in the order of the boxdict? Idk I want the 'main' box to always be first
#or perhaps thats a lost cause since in some levels the main boxes shift
#so we just go with the order of the boxdict(and if that doesnt look good, reverse order)

#pseudoboxes
#pseudoboxes are boxes that has no true interior
#like clones, reflections, infinities, and so on.
#later on these pseudoboxes can have independent properties such as possession, but they dont have their own meaningful interiors
#for these, I think I will give them names that points them to their source boxes
#Iname for infinity of name, C name for clone of name, Rname for reflection of name, and so on
#So like, IIILA or CRLB and stuff. There is going to be things in the import that decodes these names and implements them

#give exit and push an infinite loop clause
#exit first
#exit now takes into account all the box the block has attempted exit from in this turn, and stores them in a list by name.
#if the next box it is attempt to exit from is in that list, then it is determined to be an infinite exit
#an infinity box is generated with its container void, and the block exits into the void

#Ok uhh thats not good
#I realized that a pushlist needs to be present in enter and exit as well in order to handle cycles
#otherwise the pushlist gets reset and we still get infinite pushing
#hmmm

#ok stuff for tommorw
#every time push is invoked, the pushlist is checked
#its newest element is compared to every element in the pushlist before it, and if any of them are the new element, then we have a cycle
#the list from the first occurence to right before the newest element is cut into its own list
#every block in that list gets the next block's location and the last gets the first to cycle

#Colors
# Boxes have their color stored in the dims section of the export string
# format is length, width, R, G, B
# if no color is specified, default to (50,150,250)
# patrick color and pushable color are not box dependent, they are game-dependent
# will be stored at the beginning of the game export string as its own section
# if the first secion is not a specification, it is presumed to be default specs
# specs in format SPEC:Patrick Colors:Pushable Colors:additional future specs (i.e the appendix gamerules) 

#Basic Level Select
#Need to learn how to make a text input

#Compression rework
#current compression is pretty bad ngl
#names of boxes shouldnt be used to store info as it gets long and clunky. Store box infos elsewhere
#Game code structure: Specs|Box1|Box2|Box3...
#Specs: SPEC:PatColR,PatColG,PatColB:PushColR,PushColG,PushColB:additional specs...
#Box encoding: BoxSpecs:LookupData:Table:Goals
#BoxSpecs: BoxName:Rows,Cols,R,G,B,Special features(Void levels, flips, possessible, etc)
#maybe possession should be tile tier as walls and pushables can be possessible too?
#or just have #p and +p denote possessible walls and pushables, as possessible boxes can have possessible in boxspecs
#pseudoboxes like clones and infinities are defined with solely BoxSpec and nothing else as they have no interior
#LookupData: numbers with box names attached to them like 0=#,1=+,2=p0,3=VILA,4=CLB,etcetcetc
#Table: RLE compressed table data using the lookup data
#like 1*4,2*1,3*1,4*10,etcetcetc
#Goals: B1-5,P2-3,etcetcetc
#wait since we are using 4th degree denoters anyways why not just merge them all into , so like |,:,;,, instead of making 3 extra denoters
#0,#;1,+;2,p0;3,ILB;4,CLB|1*4;2*1;3*1;4*10|B,1,5;P,2,3
#yeah that seems better
#outside of "simple" boxes which do need names to distingulish them, I think the display name for dependent boxes should be separate from their internal code name when on display
#but interally they will still have their full names for coding purposes
#like box CLB will still be called CLB internally, but when displayed it will just be called B
#why do we need boxdict again? Isnt a list of boxes enough?
#ok we might just switch to a list since in a list you can go in reverse or something
#nvm boxdict is useful for lookups in cycle and infinity detection

#Clones
#Ok I thought it was just enterin that needs a minor tweak to make it work
#but I discovered something troubling
#there can be multiple clones of a box in a level
#but each clone object has to have its own location state so they must be distinct
#but they have the same attributes otherwise
#uhoh
#ok new plan
#clones are only treated the same in levelcodes
#as string doesnt store internal location
#but import installs each clone appearance as a unique object, and export removes that uniqueness
#ok current plan is that they are still effectively the same object
#just deepcopies of the original generated clone
#same name, same extension, etc
#it is just that gdict will mark them different. gdict names doesnt really matter theorhetically
#though I might be proven wrong.
#oh well we will see what's wrong when we actually make clone stuff


#phase 1: sokoban(emulating all of intro without nested boxes)
#define the print function for a given box, the movement of a player, and general mechanics of pushing
   #subphase 1.1: create compact encoding for boxes and games, also ability to import/export levels for ease of testing 
   #subphase 1.2: create block and player goals, detect if win condition is met
   #subphase 1.3: helper functions to create levels more easily
   #subphase 1.4: Undo/Redo and reset
#Implementation Successful!
#game emulated up to Intro 4

#phase 2: Enter 
#define boxes inside boxes, how to enter and exit boxes, and so on. Emulates all intro and enter level up to the first recursion level
   #subphase 2.1: Implement nested boxes into gamestate, print, and string compression
   #subphase 2.2: Implement entering and exiting boxes, push inside and outside boxes ok perfect it works
   #subphase 2.3: revamp the box system
#implementation Successful!
#game emulated up to Empty 12

#phase 3: empty
#the first level with infinity paradoxes and cyclic exits are possible.
#need to implement cycle detection and proper infinity box handling
   #subphase 3.1: implement pseudoboxes, boxes that has no interior except those of another box
   #subphase 3.2: implement cycle detection to prevent infinite loops
   #subphase 3.3: implement a special 'void' box that blocks entering any boxes within it
   #subphase 3.4: implement an emergency protocol that generates an infinity box in a void box to solve the paradox
   #subphase 3.5: implement push cycles
#implementation Successful!
#game emulated up to Eat 1

#phase 4: Eat
#define pushing boxes onto other boxes to "eat" them
#bugs detected
#cycles are valid actions despite nothing happening outside the cycle, so no other things like eats or enters should occur
#implementation Successful!
#game emulated up to Clone 1

#phase 5: UI upgrade
#add ability to get colors for boxes
#add ability to change colors of patricks and such
#(perhaps patrick and block palettes are game-dependent, while box colors, walls, floors, and goals are box-dependent)
#option for wall texturing to distingulish borders from boxes of the same color
#level select? world hub?
#better compression algorithm maybe? RLE?

#complete for now, will wait until all levels implemented before going to clone

#phase 6: Level editor
#mainly just to make these levels easier to make cause typing this shit out by commands is a pain
#need to figure out how to do number prompts
#ok plan
#always split between top and bottom. Top for display and data slots and stuff, bottom for palletes be it block or color

#Ok going back on the color thing
#I think using chatgpt to identify colors is honestly a bit dumb
#so Im gonna go back and record every color verbatim
#and sort them into chapter sections
#maybe I do a search function as well?


#Test Functions

#Test Levels
   #phase 1 test levels
def makegame1():
    root=boxes(7,7)
    root.place(1,1,patrick(0))
    root.place(1,2,patrick(1))
    root.place(2,4,pushable())
    root.place(4,4,wall())
    return game(root)
   #phase 2 test levels
ImportTest1='LR:3,3:LA,1,1|LA:3,3'
ExitTest1='LR:5,5:LA,3,3|LA:3,3:p0,1,1'
RecurseTest1='LR:5,5:p0,1,2:LR,2,2:B,3,3'
InfTest1='VILR:7,7:ILR,3,3:LR,4,3|LR:5,5:B,3,3:p0,4,2'
InfTest1N='SPEC:200,10,120:250,210,20|VILR;7,7;0,0,0;V:0,_;1,ILR;2,LR:0,24;1,1;0,6;2,1;0,17|LR;5,5;50,150,250:0,_;1,p0:0,22;1,1;0,2:B,3,3|ILR;I,LR,1'

EatTest1='LB:3,3:#,0,0:#,0,1:#,0,2:B,1,0:#,1,1:P,1,2:#,2,0:#,2,1:#,2,2|LA:7,7:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,1,0:#,1,6:#,2,0:+,2,1:LB,2,2:p0,2,3:#,2,6:#,3,0:#,3,6:#,4,0:#,4,6:#,5,0:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6'
   #Patrick's Parabox official level storage

CloneTest1='SPEC:200,10,120:250,190,60|LA;7,7;120,210,40:0,#;1,_;2,LA;3,p0;4,CLA:0,8;1,5;0,2;1,1;2,1;1,1;3,1;1,1;0,2;1,5;0,2;4,5;0,2;1,5;0,8:B,1,2;P,1,1|CLA;C,LA'
                 
#from now on I am skipping levels and only covering what can cause issues with current code
#maybe I will bother with the rest of the levels later but I want to do eat stuff now
Empty8='LB:7,7:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,1,0:#,1,1:#,1,2:B,1,3:#,1,4:#,1,5:#,1,6:#,2,0:#,2,1:#,2,2:#,2,4:#,2,5:#,2,6:#,3,0:B,3,1:LA,3,3:B,3,5:#,3,6:#,4,0:#,4,1:#,4,2:#,4,4:#,4,5:#,4,6:#,5,0:#,5,1:#,5,2:B,5,3:#,5,4:#,5,5:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6|LA:5,5:+,1,1:+,1,3:P,2,2:+,3,1:p0,3,3'
Empty12='LA:9,9:#,0,0:#,0,1:#,0,2:#,0,3:#,0,5:#,0,6:#,0,7:#,0,8:#,1,0:#,1,1:#,1,2:#,1,3:#,1,5:#,1,7:#,1,8:#,2,0:+,2,3:LA,2,5:#,2,8:#,3,0:#,3,8:#,4,0:#,4,8:#,5,0:B,5,3:P,5,4:B,5,5:#,5,8:#,6,0:p0,6,4:#,6,8:#,7,0:#,7,8:#,8,0:#,8,1:#,8,2:#,8,3:#,8,4:#,8,5:#,8,6:#,8,7:#,8,8'
Empty12N='SPEC:225,90,40:180,210,60|LA;9,9;100,150,210:0,#;1,_;2,+;3,LA;4,p0:0,4;1,1;0,8;1,1;0,1;1,1;0,3;1,2;2,1;1,1;3,1;1,2;0,2;1,7;0,2;1,7;0,2;1,7;0,2;1,3;4,1;1,3;0,2;1,7;0,10:B,5,3;B,5,5;P,5,4'

Eat1='LB:3,3:#,0,0:#,0,1:#,0,2:B,1,0:#,1,1:P,1,2:#,2,0:#,2,1:#,2,2|LA:7,7:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,1,0:#,1,6:#,2,0:LB,2,3:#,2,6:#,3,0:p0,3,1:#,3,6:#,4,0:+,4,3:#,4,6:#,5,0:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6'
Eat8='LB:3,3:#,0,0:#,0,1:#,0,2:#,1,0:P,1,1:#,1,2:#,2,0:#,2,2|LA:11,11:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,0,7:#,0,8:#,0,9:#,0,10:#,1,0:#,1,10:#,2,0:#,2,10:#,3,0:#,3,3:#,3,4:#,3,10:#,4,0:LB,4,2:#,4,4:LA,4,6:p0,4,8:#,4,10:#,5,0:#,5,2:#,5,3:#,5,4:#,6,0:+,6,1:#,6,2:#,6,10:#,7,0:#,7,1:#,7,2:#,7,9:#,7,10:#,8,0:#,8,1:#,8,2:+,8,8:#,8,10:#,9,0:#,9,1:#,9,2:#,9,8:#,9,9:#,9,10:#,10,0:#,10,1:#,10,2:#,10,3:#,10,4:#,10,6:#,10,7:#,10,8:#,10,9:#,10,10'
Eat8N='SPEC:210,110,200:250,220,130|LB;3,3;120,240,120:0,#;1,_:0,4;1,1;0,2;1,1;0,1:P,1,1|LA;11,11;100,130,230:0,#;1,_;2,LB;3,LA;4,p0;5,+:0,12;1,9;0,2;1,9;0,2;1,2;0,2;1,5;0,2;1,1;2,1;1,1;0,1;1,1;3,1;1,1;4,1;1,1;0,2;1,1;0,3;1,6;0,1;5,1;0,1;1,7;0,4;1,6;0,5;1,5;5,1;1,1;0,4;1,5;0,8;1,1;0,5'
Eat8db2='LB:3,3:#,0,0:#,0,1:#,0,2:#,1,0:P,1,1:#,1,2:#,2,0:#,2,2|LA:11,11:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,0,7:#,0,8:#,0,9:#,0,10:#,1,0:#,1,10:#,2,0:#,2,10:#,3,0:#,3,3:#,3,4:#,3,10:#,4,0:LB,4,2:#,4,4:#,4,10:#,5,0:#,5,2:#,5,3:#,5,4:#,6,0:+,6,1:#,6,2:#,6,10:#,7,0:#,7,1:#,7,2:#,7,9:#,7,10:#,8,0:#,8,1:#,8,2:p0,8,5:#,8,10:#,9,0:#,9,1:#,9,2:LA,9,5:#,9,8:#,9,9:#,9,10:#,10,0:#,10,1:#,10,2:#,10,3:#,10,4:+,10,5:#,10,6:#,10,7:#,10,8:#,10,9:#,10,10'
#bugs detected on eat8: patrick goes backwards when cycle occurs, A refuses to eat B after eating another box?
#bug 1 solved: the push function tried to enter the block but did not proceed to eat when enter failed
#changed the push code to a series of if statements instead of if-elif to allow both enter and eat to be attempted
#bug 2 solved: idk what happened, but I realized that cycles should not send out 0 signals
#as boxes recieving zero signals can still attempt to eat, enter, possess, etc
#a cycle is not the same as hitting a wall
#cycles now send out a 2 signal which is reserved for cycles and causes boxes to not attempt any actions
Eat7='LC:7,7:#,0,0:#,0,1:#,0,2:#,0,4:#,0,5:#,0,6:#,1,0:#,1,4:#,1,5:#,1,6:#,2,0:#,2,3:#,2,4:#,2,5:#,2,6:#,3,0:B,3,3:#,3,4:#,3,5:#,3,6:#,4,0:#,4,1:#,4,2:B,4,3:#,4,4:#,4,5:#,4,6:#,5,0:#,5,1:#,5,2:B,5,3:#,5,4:#,5,5:#,5,6:#,6,0:#,6,1:#,6,2:B,6,3:#,6,4:#,6,5:#,6,6|LB:3,3:#,0,0:#,0,1:#,0,2:P,1,1:#,1,2:#,2,0:#,2,1:#,2,2|LA:11,11:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,0,7:#,0,8:#,0,9:#,0,10:#,1,0:#,1,1:#,1,2:#,1,3:#,1,4:#,1,5:#,1,6:#,1,7:#,1,8:#,1,9:#,1,10:#,2,0:#,2,1:#,2,2:#,2,3:#,2,4:#,2,5:#,2,6:#,2,7:#,2,8:#,2,9:#,2,10:#,3,0:#,3,1:p0,3,5:#,3,10:#,4,0:#,4,1:#,4,10:#,5,0:#,5,1:+,5,3:LB,5,4:+,5,6:LC,5,7:+,5,8:#,5,10:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,6:#,6,7:#,6,8:#,6,9:#,6,10:#,7,0:#,7,1:#,7,2:#,7,3:#,7,4:#,7,6:#,7,7:#,7,8:#,7,9:#,7,10:#,8,0:#,8,1:#,8,2:#,8,3:#,8,4:#,8,6:#,8,7:#,8,8:#,8,9:#,8,10:#,9,0:#,9,1:#,9,2:#,9,3:#,9,4:#,9,6:#,9,7:#,9,8:#,9,9:#,9,10:#,10,0:#,10,1:#,10,2:#,10,3:#,10,4:#,10,5:#,10,6:#,10,7:#,10,8:#,10,9:#,10,10'
Eat7N='SPEC:200,10,120:250,210,20|LC;7,7;50,150,250:0,#;1,_:0,3;1,1;0,4;1,3;0,4;1,2;0,5;1,3;0,6;1,1;0,6;1,1;0,6;1,1;0,3:B,3,3;B,4,3;B,5,3;B,6,3|LB;3,3;50,150,250:0,#;1,_:0,3;1,2;0,4:P,1,1|LA;11,11;50,150,250:0,#;1,_;2,p0;3,+;4,LB;5,LC:0,35;1,3;2,1;1,4;0,3;1,8;0,3;1,1;3,1;4,1;1,1;3,1;5,1;3,1;1,1;0,6;1,1;0,10;1,1;0,10;1,1;0,10;1,1;0,16'
Reference1='LB:5,5:#,0,0:#,0,1:#,0,3:#,0,4:#,1,0:#,1,1:#,1,3:#,1,4:#,2,0:B,2,1:#,2,4:#,3,0:#,3,4:#,4,0:#,4,1:#,4,2:#,4,3:#,4,4|LA:7,7:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,1,0:P,1,5:#,1,6:#,2,0:LB,2,2:#,2,6:#,3,0:#,3,4:#,4,0:LA,4,2:p0,4,4:#,4,6:#,5,0:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6'
Reference9='LB:7,7:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,1,0:LA,1,2:#,1,6:#,2,0:#,2,6:#,3,2:#,3,6:#,4,0:+,4,4:#,4,6:#,5,0:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6|LA:9,9:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:B,0,5:#,0,7:#,0,8:#,1,0:#,1,1:#,1,2:#,1,3:#,1,4:#,1,5:#,1,7:#,1,8:#,2,0:#,2,1:#,2,2:#,2,3:#,2,4:#,2,7:#,2,8:#,3,0:#,3,1:#,3,2:#,3,3:#,3,4:#,4,5:#,3,7:#,3,8:#,4,0:#,4,1:#,4,2:#,4,3:#,4,4:LB,4,6:#,4,7:#,4,8:#,5,0:#,5,1:P,5,2:#,5,7:#,5,8:#,6,0:#,6,1:p0,6,4:#,6,7:#,6,8:#,7,0:#,7,1:#,7,7:#,7,8:#,8,0:#,8,1:#,8,2:#,8,3:#,8,5:#,8,6:#,8,7:#,8,8'
Reference10='LE:3,3:#,0,0:#,0,1:#,0,2:#,1,2:#,2,0:#,2,2|LD:5,5:#,0,0:#,0,1:#,0,3:#,0,4:#,1,0:#,1,1:B,1,2:#,1,3:#,1,4:#,2,0:#,2,1:#,2,2:#,2,3:#,2,4:#,3,0:#,3,1:P,3,2:#,3,3:#,3,4:#,4,0:#,4,1:#,4,3:#,4,4|LC:7,7:#,0,0:#,0,1:#,0,2:#,0,4:#,0,5:#,0,6:#,1,0:#,1,6:#,2,0:#,2,6:#,3,0:#,3,6:#,4,0:#,4,3:#,4,6:#,5,0:LB,5,3:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6|LB:7,7:#,0,0:#,0,1:#,0,2:LD,0,3:B,0,3:#,0,4:#,0,5:#,0,6:#,1,0:#,1,5:#,1,6:#,2,0:#,2,5:#,2,6:#,3,0:p0,3,1:LA,3,5:#,3,6:#,4,0:#,4,5:#,4,6:#,5,0:#,5,1:#,5,2:LC,5,3:#,5,4:#,5,5:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6|LA:9,9:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,0,7:#,0,8:#,1,0:#,1,1:#,1,2:#,1,3:#,1,4:#,1,5:#,1,6:#,1,7:#,1,8:#,2,0:#,2,8:#,3,0:+,3,4:+,3,6:#,3,8:#,4,2:#,4,7:#,4,8:#,5,0:+,5,4:LE,5,6:#,5,8:#,6,0:#,6,8:#,7,0:#,7,1:#,7,2:#,7,3:#,7,4:#,7,5:#,7,6:#,7,7:#,7,8:#,8,0:#,8,1:#,8,2:#,8,3:#,8,4:#,8,5:#,8,6:#,8,7:#,8,8'

Swap1='LB:7,7,50,250,150:#,0,0:#,0,1:#,0,2:#,0,4:#,0,5:#,0,6:#,1,0:#,1,6:#,2,0:B,2,1:#,2,6:#,3,0:P,3,5:#,3,6:#,4,0:B,4,1:#,4,6:#,5,0:#,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6|LA:9,9,50,150,250:#,0,0:#,0,1:#,0,2:#,0,3:#,0,4:#,0,5:#,0,6:#,0,7:#,0,8:#,1,0:#,1,8:#,2,0:p0,2,4:#,2,8:#,3,0:#,3,8:#,4,0:LA,4,3:LB,4,5:#,5,0:#,5,8:#,6,0:#,6,8:#,7,0:#,7,4:#,7,8:#,8,0:#,8,1:#,8,2:#,8,3:#,8,4:#,8,5:#,8,6:#,8,7:#,8,8'

Center6='LA:7,7:#,0,0:B,0,5:#,1,0:#,1,3:P,1,5:#,2,0:#,3,0:p0,3,3:#,3,5:#,4,0:#,5,0:LA,5,1:+,5,6:#,6,0:#,6,1:#,6,2:#,6,3:#,6,4:#,6,5:#,6,6'










