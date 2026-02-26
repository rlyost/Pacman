class LevelController(object):
    def __init__(self):
        self.level = 0
        self.levelmaps = {0: {"mazename":"maze1.txt", "pelletname":"pellets1.txt", "row":0, "fruit":"cherry"}}
        
    def nextLevel(self):
        self.level += 1
        
    def reset(self):
        self.level = 0
        
    def getLevel(self):
        return self.levelmaps[self.level % len(self.levelmaps)]

                                                                        
