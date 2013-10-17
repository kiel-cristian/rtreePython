# encoding: utf-8
'''
Created on 09-10-2013

@author: Ian
'''
from Mbr import *
from MbrPointer import *

class SelectionError(Exception):
    def __init__(self, value="partition error"):
        super(SelectionError, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)

class SelectionManager():
    def __init__(self):
        pass
    def select(self,mbrPointer, mbrPointersList):
        pass
    def radialSelect(self, radialMbr, mList):
        intersections = []
        for m in mList:
            if radialMbr.areIntersecting(m):
                intersections = intersections + [m]
        return intersections

class RtreeSelection(SelectionManager):
    def select(self,mbrPointer, mbrPointersList):
        minimum = None
        selected = None
        for mbr in mbrPointersList:
            mbrExpanded = mbrPointer.returnExpandedMBR(mbr)
            crec = mbrExpanded.getArea() - mbrPointer.getArea()
            if crec == 0:
                return mbr
            if minimum == None:
                minimum = crec
                selected = mbr
            elif crec < minimum:
                minimum = crec
                selected = mbr
        return selected

class RtreePlusSelection(SelectionManager):
    def select(self,mbrPointer, mbrPointersList):
        selected = []
        for mbr in mbrPointersList:
            if mbrPointer.areIntersecting(mbr):
                selected = selected + [mbr]
        return selected

    def selectNearest(self,mbrPointer, mbrPointersList):
        minDist  = None
        selected = None
        for mbp in mbrPointersList:
            dist = mbrPointer.distanceTo(mbp)
            if minDist == None or minDist > dist:
                minDist = dist
                selected = mbp
        return selected

    def selectAny(self, mbrPointersList):
        for mbr in mbrPointersList:
            if mbr.getPointer() != -1:
                return mbr

def newMbrPointer(point):
    return MbrPointer(Mbr(2).setPoint(point), 0)

if __name__ == "__main__":
    parent = newMbrPointer([0.5,0.5])
    parent.setRange([0.1,0.7,0.3,0.6])
    mList = [newMbrPointer([0.8, 0.8]).setRange([0.7, 0.9, 0.7,0.9])
           , newMbrPointer([0.2, 0.5]).setRange([0.1, 0.3, 0.4,0.6])
           , newMbrPointer([0.8, 0.5]).setRange([0.7, 0.9, 0.4,0.6])]
    print([str(_) for _ in mList])
    print("Rtree")
    print(str(RtreeSelection().select(parent, mList)))
    print("Rtree+")
    print([ str(_) for _ in RtreePlusSelection().select(parent, mList)])
