import random
from MbrApi import *
from Mbr import Mbr

class MbrPointer(MbrApi):
    def __init__(self, mbr, pointer):
        super(MbrPointer, self).__init__()
        self.mbr         = mbr
        self.pointer = pointer
    def __str__(self):
        return "[MbrPointer]{ mbr: " + str(self.mbr) + ", p: " + str(self.pointer) + "}"
    def getMin(self,d):
        return self.mbr.getMin(d)
    def getMax(self,d):
        return self.mbr.getMax(d)
    def getPointer(self):
        return self.pointer
    def getMbr(self):
        return self.mbr
    def setRange(self, o):
        self.mbr.setRange(o)
        return self
    def distanceTo(self, mbrPointer):
        return self.getMbr().distanceTo(mbrPointer.getMbr())
    def returnExpandedMBR(self, mbrPointer):
        return self.getMbr().returnExpandedMBR(mbrPointer.getMbr())
    def getArea(self):
        return self.getMbr().getArea()
    def deadSpace(self, mbrPointer):
        return self.getMbr().deadSpace(mbrPointer.getMbr())
    def areIntersecting(self,mbrPointer):
        return self.getMbr().areIntersecting(mbrPointer.getMbr())
    def getCenter(self):
        return self.getMbr().getCenter()

def randomMbrPointer(d):
    randomPoint = [random.random() for _ in range(d)]
    return MbrPointer(Mbr(d).setPoint(randomPoint), int(randomPoint[0]*1000))