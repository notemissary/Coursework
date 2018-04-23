# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 14:52:46 2017

@author: noname
"""
import random as r


prevVer1 = 0
prevVer2 = 0


class Fractal:
    def __init__(self, x, y, vertexes, allowed):
        # print('Hola')
        self.x = x+4
        self.y = y+4
        self.allowed = allowed
        self.vertexes = vertexes
        self.verList = list(self.vertexes.keys())
        self.flag = False
        self.draw()

    def coordinates(self):
        return self.x, self.y, self.vertexes[prevVer1]

    def draw(self):
        global prevVer1
        while True:
            t = r.SystemRandom().choice(self.verList)
            if abs(t - prevVer1) in self.allowed:
                prevVer1 = t
                t = self.vertexes[t]
                break
        x, y = t.pos().x(), t.pos().y()
        self.x, self.y = mid_point(self.x, self.y, x, y, 1)


def mid_point(x1, y1, x2, y2, k):
    x = (x1 + x2*k) / (1 + k)
    y = (y1 + y2*k) / (1 + k)
    return int(round(x)), int(round(y))
