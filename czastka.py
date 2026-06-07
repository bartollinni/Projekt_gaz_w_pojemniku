import random
import math

class Czastka:
    def __init__(self, x, y, promien=5, masa=1):
        self.x = x
        self.y = y

        self.promien = promien
        self.masa = masa

        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)


    def ruch(self):
        self.x += self.vx
        self.y += self.vy

    def czy_sciana(self, dlugosc_podstawy, wysokosc_sciany):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
