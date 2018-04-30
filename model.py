# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 14:52:46 2017

This file contains main algorithm for calculating a point coordinates according to given rules of Chaos Game method.

@author: Dyma Volodymyr Sergiyovoich
"""
import secrets as s

prevVer1 = 0


class Fractal:
    """Fractal class

    This class is used to calculating a point coordinates according to given rules.

    :param x and y: are coordinates of the last placed point.
    :param vertexes: is a dictionary of the vertexes available for moving to
    :param allowed: is a list of allowed gaps between the previously chosen vertex and currently chosen one
    """
    def __init__(self, x, y, vertexes, allowed, relation):
        assert isinstance(x, int) and isinstance(y, int), 'x and y type must be integer'
        assert isinstance(vertexes, dict), 'vertexes type must be dict'
        assert isinstance(allowed, list), 'allowed type must be list'
        assert isinstance(relation, float), 'relation type must be float'
        self.x = x + 4
        self.y = y + 4
        self.allowed = allowed
        self.vertexes = vertexes
        self.relation = relation
        self.draw()

    def coordinates(self):
        """Returns coordinates and a chosen vertex

        :return: list of x coord, y coord and currently chosen vertex object
        """
        return self.x, self.y, self.vertexes[prevVer1]

    def draw(self):
        """Calculates coords to move to
        """
        global prevVer1
        while True:
            t = s.choice(list(self.vertexes.keys()))
            if abs(t - prevVer1) in self.allowed:
                prevVer1 = t
                t = self.vertexes[t]
                break
        x, y = t.pos().x(), t.pos().y()
        self.x, self.y = self.mid_point(self.x, self.y, x, y, self.relation)

    @staticmethod
    def mid_point(x1, y1, x2, y2, k):
        """Calculate a midpoint

        This method calculate a midpoint between two given points.

        :param x1: x coord of the first point
        :param y1: y coord of the second point
        :param x2: x coord of the first point
        :param y2: y coord of the second point
        :param k: relation ratio
        :return: list of two integers representing coordinates of midpoint
        """
        assert isinstance(x1, int) and isinstance(x2, int) and isinstance(y1, int) and isinstance(y1, int), \
            'x1, y1, x2, y2 types must be integer'
        assert isinstance(k, float), 'k type must be float'
        x = (x1 + x2*k) / (1 + k)
        y = (y1 + y2*k) / (1 + k)
        return int(round(x)), int(round(y))
