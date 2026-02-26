import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from animation import Animation

class Pacman(Entity):
    def __init__(self, nodes, spritesheet):
        Entity.__init__(self, nodes, spritesheet)
        self.name = "pacman"
        self.color = YELLOW
        self.setStartPosition()
        self.lives = 5
        self.animation = None
        self.animations = {}
        self.dying = False
        self.defineAnimations()
        self.startImage = self.getSprite(4, 0)
        self.image = self.startImage
        self.lifeicons = self.getSprite(0, 0)

    def reset(self):
        self.setStartPosition()
        self.image = self.startImage
        self.dying = False
        self.animations["death"].reset()

    def loseLife(self):
        self.lives -= 1

    def die(self):
        self.loseLife()
        self.dying = True
        self.animations["death"].reset()

    def renderLives(self, screen):
        for i in range(self.lives-1):
            x = 10 + 36 * i
            y = TILEHEIGHT * NROWS - 36
            screen.blit(self.lifeicons, (x, y))

    def update(self, dt):
        self.visible = True
        self.position += self.direction*self.speed*dt
        self.updateAnimation(dt)
        direction = self.getValidKey()
        if direction:
            self.moveByKey(direction)
        else:
            self.moveBySelf()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return None

    def moveByKey(self, direction):
        if self.direction is STOP:
            if self.node.neighbors[direction] is not None:
                self.target = self.node.neighbors[direction]
                self.direction = direction
        else:
            if direction == self.direction * -1:
                self.reverseDirection()
            if self.overshotTarget():
                self.node = self.target
                self.portal()
                if self.node.neighbors[direction] is not None:
                    if self.node.homeEntrance:
                        if self.node.neighbors[self.direction] is not None:
                            self.target = self.node.neighbors[self.direction]
                        else:
                            self.setPosition()
                            self.direction = STOP
                    else:
                        self.target = self.node.neighbors[direction]
                        if self.direction != direction:
                            self.setPosition()
                            self.direction = direction
                else:
                    if self.node.neighbors[self.direction] is not None:
                        self.target = self.node.neighbors[self.direction]
                    else:
                        self.setPosition()
                        self.direction = STOP

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius+self.collideRadius)**2
            if dSquared <= rSquared:
                return pellet
        return None

    def eatGhost(self, ghosts):
        for ghost in ghosts:
            d = self.position - ghost.position
            dSquared = d.magnitudeSquared()
            rSquared = (self.collideRadius + ghost.collideRadius)**2
            if dSquared <= rSquared:
                return ghost
        return None

    def eatFruit(self, fruit):
        d = self.position - fruit.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius+fruit.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.pacmanStartNode:
                return node
        return None

    def setStartPosition(self):
        self.direction = LEFT
        self.node = self.findStartNode()
        self.target = self.node.neighbors[self.direction]
        self.setPosition()
        self.position.x -= (self.node.position.x - self.target.position.x) / 2

    def getSprite(self, col, row):
        img = self.spritesheet.getImage(col, row, 32, 32)
        return pygame.transform.scale(img, (28, 28))

    def defineAnimations(self):
        # Sprite layout (32x32 native, scaled to 28x28):
        # col0=LEFT (small=row0, wide=row1), col1=RIGHT (small=row0, wide=row1)
        # col2=DOWN (small=row1, wide=row0), col3=UP (small=row1, wide=row0), col4=CLOSED
        # Row 7: death animation cols 0-8, 10

        anim = Animation("loop")
        anim.speed = 30
        anim.addFrame(self.getSprite(4, 0))  # closed
        anim.addFrame(self.getSprite(0, 0))  # left small  (col0,row0)
        anim.addFrame(self.getSprite(0, 1))  # left wide   (col0,row1)
        anim.addFrame(self.getSprite(0, 0))  # left small
        self.animations["left"] = anim

        anim = Animation("loop")
        anim.speed = 30
        anim.addFrame(self.getSprite(4, 0))  # closed
        anim.addFrame(self.getSprite(1, 0))  # right small (col1,row0)
        anim.addFrame(self.getSprite(1, 1))  # right wide  (col1,row1)
        anim.addFrame(self.getSprite(1, 0))  # right small
        self.animations["right"] = anim

        anim = Animation("loop")
        anim.speed = 30
        anim.addFrame(self.getSprite(4, 0))  # closed
        anim.addFrame(self.getSprite(2, 1))  # down small
        anim.addFrame(self.getSprite(2, 0))  # down wide
        anim.addFrame(self.getSprite(2, 1))  # down small
        self.animations["down"] = anim

        anim = Animation("loop")
        anim.speed = 30
        anim.addFrame(self.getSprite(4, 0))  # closed
        anim.addFrame(self.getSprite(3, 1))  # up small
        anim.addFrame(self.getSprite(3, 0))  # up wide
        anim.addFrame(self.getSprite(3, 1))  # up small
        self.animations["up"] = anim

        anim = Animation("once")
        anim.speed = 10
        for col in range(9):
            anim.addFrame(self.getSprite(col, 7))
        anim.addFrame(self.getSprite(10, 7))
        self.animations["death"] = anim

        anim = Animation("static")
        anim.addFrame(self.getSprite(4, 0))  # closed
        self.animations["idle"] = anim

    def updateAnimation(self, dt):
        if self.dying:
            self.animation = self.animations["death"]
        elif self.direction == UP:
            self.animation = self.animations["up"]
        elif self.direction == DOWN:
            self.animation = self.animations["down"]
        elif self.direction == LEFT:
            self.animation = self.animations["left"]
        elif self.direction == RIGHT:
            self.animation = self.animations["right"]
        elif self.direction == STOP:
            self.animation = self.animations["idle"]
        self.image = self.animation.update(dt)
