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

    def zderzenie(self, inna_czastka):
        if (self.x-inna_czastka.x)**2+(self.y-inna_czastka.y)**2 <= (self.promien+inna_czastka.promien):
            kat_zderzenia=math.atan((self.y-inna_czastka.y)/(self.x-inna_czastka.x))
            # wszelkie u to placeholdery na prędkości w układzie pod kątem zderzenia 
            ux_self=cos(kat_zderzenia)*self.vx+sin(kat_zderzenia)*self.vy
            uy_self=sin(kat_zderzenia)*self.vx+cos(kat_zderzenia)*self.vy
            ux_czastka=cos(kat_zderzenia)*inna_czastka.vx+sin(kat_zderzenia)*inna_czastka.vy
            uy_czastka=sin(kat_zderzenia)*inna_czastka.vx+cos(kat_zderzenia)*inna_czastka.vy

            self.vx=sin(kat_zderzenia)*uy_self+cos(kat_zderzenia)*ux_czastka
            self.vy=cos(kat_zderzenia)*uy_self+sin(kat_zderzenia)*ux_czastka
            inna_czastka.vx=sin(kat_zderzenia)*uy_czastka+cos(kat_zderzenia)*ux_self
            inna_czastka.vy=cos(kat_zderzenia)*uy_czastka+sin(kat_zderzenia)*ux_self
            
