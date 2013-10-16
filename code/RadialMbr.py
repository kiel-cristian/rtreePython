from math import sqrt
from math import pi
from MbrApi import *


class RadialMbr(MbrApi):
    def __init__(self, d, point, r):
        super(RadialMbr, self).__init__()
        self.d            = d
        self.center = point
        self.r            = r
    def __str__(self):
        return "[RadialMbr]{ center: " + str(self.center) + ", r: " + str(self.r) + "}"
    def getMin(self,d):
        return self.center[d]
    def getMax(self,d):
        return self.center[d] + self.r
    def getR(self):
        return self.r
    def getCenter(self):
        return self.center
    def setCenter(self, p):
        self.center = p
    def setR(self,r):
        self.r = r
    def distanceTo(self, mbrObject):
        mbrCenter    = mbrObject.getCenter()
        thisCenter = self.getCenter()
        delta = 0
        for d in range(self.d):
            delta = delta + (mbrCenter[d] - thisCenter[d])**2
        return sqrt(delta)
    def getArea(self):
        return pi*self.r**2/2
    def areIntersecting(self,mbrObject):
        return self.distanceTo(mbrObject) <= self.r