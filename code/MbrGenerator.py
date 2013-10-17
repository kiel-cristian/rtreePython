from MbrPointer import *
from RadialMbr import *
from random import random

class MbrGenerator(object):
    def __init__(self):
        self.lastId = 0

    def next(self, d):
        randomPoint = [random() for _ in range(d)]
        nextMbrPointer = MbrPointer( Mbr(d).setPoint(randomPoint), self.lastId)
        self.lastId = self.lastId + 1
        return nextMbrPointer

    def nextRadial(self, d, r):
        return RadialMbr(d, [random() for _ in range(d)], r)