import random
import math
import numpy as np

class Czastka:
    def __init__(self, x, y, masa=1, dt):
        self.x = x
        self.y = y
        self.masa = masa

        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)


    def ruch(self):
        self.x += self.vx*dt
        self.y += self.vy*dt

    def czy_sciana(self, dlugosc_podstawy, wysokosc_sciany):
        if np.absolute(self.x) > dlugosc_podstawy/2:
            self.vx *= -1
        if np.absolute(self.y) > dlugosc_podstawy/2:
            self.vy *= -1
            
