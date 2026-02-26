import pygame
from constants import *

class Maze(object):
    def __init__(self, spritesheet):
        self.spritesheet = spritesheet
        self.spriteInfo = None
        self.rotateInfo = None
        self.images = []
        self.flash_images = []
        self.imageRow = 16
        
    def getMazeImages(self, row=0):
        self.images = []
        for i in range(11):
            self.images.append(self.spritesheet.getImage(i, self.imageRow+row, TILEWIDTH, TILEHEIGHT))
            
    def rotate(self, image, value):
        return pygame.transform.rotate(image, value*90)
    
    def readMazeFile(self, textfile):
        f = open(textfile, "r")
        lines = [line.rstrip('\n') for line in f]
        return [line.split(' ') for line in lines]
    
    def getMaze(self, mazename):
        self.spriteInfo = self.readMazeFile(mazename+"_sprites.txt")
        self.rotateInfo = self.readMazeFile(mazename+"_rotation.txt")
        
    def constructMaze(self, background, row=0):
        self.getMazeImages(row)
        rows = len(self.spriteInfo)
        cols = len(self.spriteInfo[0])
        for row in range(rows):
            for col in range(cols):
                x = col * TILEWIDTH
                y = row * TILEHEIGHT
                val = self.spriteInfo[row][col]
                if val.isdecimal():
                    rotVal = self.rotateInfo[row][col]
                    image = self.rotate(self.images[int(val)], int(rotVal))
                    background.blit(image, (x, y))
                    
                if val == '=':
                    background.blit(self.images[10], (x, y))
