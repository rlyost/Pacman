import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pauser
from levels import LevelController
from text import TextGroup
from sprites import Spritesheet
from maze import Maze

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, pygame.SCALED | pygame.RESIZABLE)
        self.background = None
        self.setBackground()
        self.clock = pygame.time.Clock()
        self.pelletsEaten = 0
        self.fruit = None
        self.pause = Pauser(True)
        self.level = LevelController()
        self.text = TextGroup()
        self.sheet = Spritesheet()
        self.maze = Maze(self.sheet)
        
    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        self.level.reset()
        levelmap = self.level.getLevel()
        self.maze.getMaze(levelmap["mazename"].split(".")[0])
        self.maze.constructMaze(self.background)
        self.nodes = NodeGroup(levelmap["mazename"])
        self.pellets = PelletGroup(levelmap["pelletname"])
        self.pacman = Pacman(self.nodes, self.sheet)
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.pelletsEaten = 0
        self.fruit = None
        self.pause.force(True)
        self.gameover = False
        self.score = 0
        self.text.showReady()
        self.text.updateLevel(self.level.level+1)
        
    def startLevel(self):
        levelmap = self.level.getLevel()
        self.setBackground()
        self.maze.getMaze(levelmap["mazename"].split(".")[0])
        self.maze.constructMaze(self.background)
        self.nodes = NodeGroup(levelmap["mazename"])
        self.pellets = PelletGroup(levelmap["pelletname"])
        self.pacman.nodes = self.nodes
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.pelletsEaten = 0
        self.fruit = None
        self.pause.force(True)
        self.text.showReady()
        self.text.updateLevel(self.level.level+1)

    def restartLevel(self):
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.fruit = None
        self.pause.force(True)
        self.text.showReady()
        
    def update(self):
        dt = self.clock.tick(30) / 1000.0
        if not self.gameover:
            if not self.pause.paused:
                self.pacman.update(dt)
                self.ghosts.update(dt, self.pacman)
                if self.fruit is not None:
                    self.fruit.update(dt)
                if self.pause.pauseType != None:
                    self.pause.settlePause(self)
                self.checkPelletEvents()
                self.checkGhostEvents()
                self.checkFruitEvents()
            elif self.pacman.dying:
                self.pacman.updateAnimation(dt)

            self.pause.update(dt)
            self.pellets.update(dt)
            self.text.update(dt)
        self.checkEvents()
        self.text.updateScore(self.score)
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.gameover:
                        self.startGame()
                    else:
                        self.pause.player()
                        if self.pause.paused:
                            self.text.showPause()
                        else:
                            self.text.hideMessages()

    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pelletsEaten += 1
            self.score += pellet.points
            if (self.pelletsEaten == 70 or self.pelletsEaten == 140):
                if self.fruit is None:
                    self.fruit = Fruit(self.nodes, self.sheet)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == "powerpellet":
                self.ghosts.resetPoints()
                self.ghosts.freightMode()
            if self.pellets.isEmpty():
                self.pacman.visible = False
                self.ghosts.hide()
                self.pause.startTimer(3, "clear")
                
    def checkGhostEvents(self):
        self.ghosts.release(self.pelletsEaten)
        ghost = self.pacman.eatGhost(self.ghosts)
        if ghost is not None:
            if ghost.mode.name == "FREIGHT":
                self.score += ghost.points
                self.text.createTemp(ghost.points, ghost.position)
                self.ghosts.updatePoints()
                ghost.spawnMode(speed=2)
                self.pause.startTimer(1)
                self.pacman.visible = False
                ghost.visible = False
            elif ghost.mode.name == "CHASE" or ghost.mode.name == "SCATTER":
                self.pacman.die()
                self.ghosts.hide()
                self.pause.startTimer(3, "die")

    def checkFruitEvents(self):
        if self.fruit is not None:
            if self.pacman.eatFruit(self.fruit):
                self.score += self.fruit.points
                self.text.createTemp(self.fruit.points, self.fruit.position)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None
            #if self.pacman.eatFruit(self.fruit) or self.fruit.destroy:
                #self.fruit = None

    def resolveDeath(self):
        if self.pacman.lives == 0:
            self.gameover = True
            self.text.showGameOver()
        else:
            self.restartLevel()
        self.pause.pauseType = None

    def resolveLevelClear(self):
        self.level.nextLevel()
        self.startLevel()
        self.pause.pauseType = None
    
    def render(self):
        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.pacman.renderLives(self.screen)
        self.text.render(self.screen)
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
