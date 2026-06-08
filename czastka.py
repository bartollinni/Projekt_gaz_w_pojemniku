import random
import math
from naczynie import sciana_prawa_x, sciana_dolna_y

class Czastka:
    def __init__(self, x, y, promien=1, masa=1):
        self.x = x
        self.y = y

        self.promien = promien
        self.masa = masa

        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)


    def ruch(self):
        self.x += self.vx
        self.y += self.vy

    def czy_sciana(self):
        # sciana x=0
        if self.x - self.promien < 0:
            self.x = self.promien
            self.vx =  -1 * self.vx
        # sciana x=(coś)
        elif self.x + self.promien > sciana_prawa_x:
            self.x = sciana_prawa_x - self.promien
            self.vx = -1 * self.vx
        # sciana y =(coś)
        if self.y + self.promien > sciana_dolna_y:
            self.y = sciana_dolna_y - self.promien
            self.vy = -1 * self.vy
        #sciana y=0
        elif self.y - self.promien< 0:
            self.y = self.promien
            self.vy = -1 * self.vy
