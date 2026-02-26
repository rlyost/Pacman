import pygame
from entity import Entity
from constants import *
from vector import Vector2
from random import randint
from modes import Mode
from stack import Stack
from animation import Animation

class Ghost(Entity):
    def __init__(self, nodes, spritesheet):
        Entity.__init__(self, nodes, spritesheet)
        self.name = "ghost"
        self.goal = Vector2()
        self.points = 200
        self.modeStack = self.setupModeStack()
        self.mode = self.modeStack.pop()
        self.modeTimer = 0
        self.spawnNode = self.findSpawnNode()
        self.setGuideStack()
        self.pelletsForRelease = 0
        self.released = True
        self.bannedDirections = []
        self.animation = None
        self.animations = {}
        
    def update(self, dt, pacman, blinky=None):
        self.visible = True
        self.portalSlowdown()
        speedMod = self.speed * self.mode.speedMult
        self.position += self.direction*speedMod*dt
        self.modeUpdate(dt)
        if self.mode.name == "CHASE":
            self.chaseGoal(pacman, blinky)
        elif self.mode.name == "SCATTER":
            self.scatterGoal()
        elif self.mode.name == "FREIGHT":
            self.randomGoal()
        elif self.mode.name == "SPAWN":
            self.spawnGoal()
        self.moveBySelf()
        self.updateAnimation(dt)
        
    def getValidDirections(self):
        validDirections = []
        for key in self.node.neighbors.keys():
            if self.node.neighbors[key] is not None:
                if key != self.direction * -1:
                    if not self.mode.name == "SPAWN":
                        if not self.node.homeEntrance:
                            if key not in self.bannedDirections:
                                validDirections.append(key)
                        else:
                            if key != DOWN:
                                validDirections.append(key)
                    else:
                        validDirections.append(key)
        if len(validDirections) == 0:
            validDirections.append(self.forceBacktrack())
        return validDirections
    
    def randomDirection(self, validDirections):
        index = randint(0, len(validDirections) - 1)
        return validDirections[index]

    def getClosestDirection(self, validDirections):
        distances = []
        for direction in validDirections:
            diffVec = self.node.position + direction*TILEWIDTH - self.goal
            distances.append(diffVec.magnitudeSquared())
        index = distances.index(min(distances))
        return validDirections[index]
    
    def moveBySelf(self):
        if self.overshotTarget():
            self.node = self.target
            self.portal()
            validDirections = self.getValidDirections()
            self.direction = self.getClosestDirection(validDirections)
            self.target = self.node.neighbors[self.direction]
            self.setPosition()
            if self.mode.name == "SPAWN":
                if self.position == self.goal:
                    self.mode = self.modeStack.pop()
                    self.direction = self.mode.direction
                    self.target = self.node.neighbors[self.direction]
                    self.setPosition()
            elif self.mode.name == "GUIDE":
                self.mode = self.modeStack.pop()
                if self.mode.name == "GUIDE":
                    self.direction = self.mode.direction
                    self.target = self.node.neighbors[self.direction]
                    self.setPosition()
            
    def forceBacktrack(self):
        if self.direction * -1 == UP:
            return UP
        if self.direction * -1 == DOWN:
            return DOWN
        if self.direction * -1 == LEFT:
            return LEFT
        if self.direction * -1 == RIGHT:
            return RIGHT
        
    def portalSlowdown(self):
        self.speed = 100
        if self.node.portalNode or self.target.portalNode:
            self.speed = 50

    def setupModeStack(self):
        modes = Stack()
        modes.push(Mode(name="CHASE"))
        modes.push(Mode(name="SCATTER", time=5))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        return modes
    
    def scatterGoal(self):
        self.goal = Vector2(SCREENSIZE[0], 0)
        
    def chaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position

    def randomGoal(self):
        x = randint(0, NCOLS*TILEWIDTH)
        y = randint(0, NROWS*TILEHEIGHT)
        self.goal = Vector2(x, y)
                    
    def modeUpdate(self, dt):
        self.modeTimer += dt
        if self.mode.time is not None:
            if self.modeTimer >= self.mode.time:
                self.reverseDirection()
                self.mode = self.modeStack.pop()
                self.modeTimer = 0

    def freightMode(self):
        if self.mode.name != "SPAWN" and self.mode.name != "GUIDE":
            if self.mode.name != "FREIGHT":
                if self.mode.time is not None:
                    dt = self.mode.time - self.modeTimer
                    self.modeStack.push(Mode(name=self.mode.name, time=dt))
                else:
                    self.modeStack.push(Mode(name=self.mode.name))
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            else:
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            self.reverseDirection()

    def spawnMode(self, speed=1):
        self.mode = Mode("SPAWN", speedMult=speed)
        self.modeTimer = 0
        for d in self.guide:
            self.modeStack.push(Mode("GUIDE", speedMult=0.5, direction=d))
            
    def findSpawnNode(self):
        for node in self.nodes.homeList:
            if node.spawnNode:
                break
        return node
    
    def spawnGoal(self):
        self.goal = self.spawnNode.position

    def setGuideStack(self):
        self.guide = [UP]

    def reverseDirection(self):
        if self.mode.name != "GUIDE" and self.mode.name != "SPAWN":
            Entity.reverseDirection(self)

    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node
        self.setPosition()

    def defineAnimations(self, row):
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, row, 32, 32))
        self.animations["up"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(2, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, row, 32, 32))
        self.animations["down"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(4, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(5, row, 32, 32))
        self.animations["left"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(6, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(7, row, 32, 32))
        self.animations["right"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 6, 32, 32))
        self.animations["freight"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(2, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, 6, 32, 32))
        self.animations["flash"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(4, 6, 32, 32))
        self.animations["spawnup"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(5, 6, 32, 32))
        self.animations["spawndown"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(6, 6, 32, 32))
        self.animations["spawnleft"] = anim

        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(7, 6, 32, 32))
        self.animations["spawnright"] = anim

    def updateAnimation(self, dt):
        if self.mode.name == "SPAWN":
            if self.direction == UP:
                self.animation = self.animations["spawnup"]
            elif self.direction == DOWN:
                self.animation = self.animations["spawndown"]
            elif self.direction == LEFT:
                self.animation = self.animations["spawnleft"]
            elif self.direction == RIGHT:
                self.animation = self.animations["spawnright"]
                
        if self.mode.name in ["CHASE", "SCATTER"]:
            if self.direction == UP:
                self.animation = self.animations["up"]
            elif self.direction == DOWN:
                self.animation = self.animations["down"]
            elif self.direction == LEFT:
                self.animation = self.animations["left"]
            elif self.direction == RIGHT:
                self.animation = self.animations["right"]
                
        if self.mode.name == "FREIGHT":
            if self.modeTimer >= (self.mode.time * 0.7):
                self.animation = self.animations["flash"]
            else:
                self.animation = self.animations["freight"]
        self.image = self.animation.update(dt)
        
                                                            

class Blinky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "blinky"
        self.color = RED
        self.setStartPosition()
        self.image = self.spritesheet.getImage(4,2,32,32)
        self.defineAnimations(2)
        self.animation = self.animations["left"]
        
    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.blinkyStartNode:
                return node
        return None

    
class Pinky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "pinky"
        self.color = PINK
        self.setStartPosition()
        self.image = self.spritesheet.getImage(0,3,32,32)
        self.defineAnimations(3)
        self.animation = self.animations["up"]
        
    def scatterGoal(self):
        self.goal = Vector2()
        
    def chaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position + pacman.direction * TILEWIDTH * 4

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.pinkyStartNode:
                return node
        return None

    
class Inky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "inky"
        self.color = TEAL
        self.setStartPosition()
        self.pelletsForRelease = 30
        self.released = False
        self.bannedDirections = [RIGHT]
        self.spawnNode = self.node
        self.image = self.spritesheet.getImage(2,4,32,32)
        self.defineAnimations(4)
        self.animation = self.animations["down"]
        
    def setGuideStack(self):
        self.guide = [UP, RIGHT]
        
    def scatterGoal(self):
        self.goal = Vector2(TILEWIDTH*NCOLS, TILEHEIGHT*NROWS)
        
    def chaseGoal(self, pacman, blinky=None):
        vec1 = pacman.position + pacman.direction * TILEWIDTH * 2
        vec2 = (vec1 - blinky.position) * 2
        self.goal = blinky.position + vec2

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.inkyStartNode:
                return node
        return None

        
class Clyde(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.name = "clyde"
        self.color = ORANGE
        self.setStartPosition()
        self.pelletsForRelease = 60
        self.released = False
        self.bannedDirections = [LEFT]
        self.spawnNode = self.node
        self.image = self.spritesheet.getImage(2,5,32,32)
        self.defineAnimations(5)
        self.animation = self.animations["down"]
        
    def setGuideStack(self):
        self.guide = [UP, LEFT]
        
    def scatterGoal(self):
        self.goal = Vector2(0, TILEHEIGHT*NROWS)
        
    def chaseGoal(self, pacman, blinky=None):
        d = pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (TILEWIDTH * 8)**2:
            self.scatterGoal()
        else:
            self.goal = pacman.position + pacman.direction * TILEWIDTH * 4

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.clydeStartNode:
                return node
        return None
    

class GhostGroup(object):
    def __init__(self, nodes, spritesheet):
        self.nodes = nodes
        self.ghosts = [Blinky(nodes, spritesheet),
                       Pinky(nodes, spritesheet),
                       Inky(nodes, spritesheet),
                       Clyde(nodes, spritesheet)]
        
    def __iter__(self):
        return iter(self.ghosts)
    
    def update(self, dt, pacman):
        for ghost in self:
            ghost.update(dt, pacman, self.ghosts[0])
            
    def freightMode(self):
        for ghost in self:
            ghost.freightMode()
            
    def updatePoints(self):
        for ghost in self:
            ghost.points *= 2
            
    def resetPoints(self):
        for ghost in self:
            ghost.points = 200
            
    def hide(self):
        for ghost in self:
            ghost.visible = False

    def release(self, numPelletsEaten):
        for ghost in self:
            if not ghost.released:
                if numPelletsEaten >= ghost.pelletsForRelease:
                    ghost.bannedDirections = []
                    ghost.spawnMode()
                    ghost.released = True
                    
    def render(self, screen):
        for ghost in self:
            ghost.render(screen)

                                                                                                    

                                                                    
