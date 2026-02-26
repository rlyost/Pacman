import pygame
from entity import Entity
from constants import *

class Fruit(Entity):
    def __init__(self, nodes, spritesheet):
        Entity.__init__(self, nodes, spritesheet)
        self.name = "fruit"
        self.color = (0,200,0)
        self.setStartPosition()
        self.lifespan = 5
        self.timer = 0
        self.destroy = False
        self.points = 100
        self.image = self.spritesheet.getImage(8, 2, TILEWIDTH, TILEHEIGHT)
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy = True
            
    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node.neighbors[LEFT]
        self.setPosition()
        self.position.x -= (self.node.position.x - self.target.position.x) / 2
        
    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.fruitStartNode:
                return node
        return None
