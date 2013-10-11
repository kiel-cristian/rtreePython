from MbrApi import *

class RadialMbr(MbrApi):
  def __init__(self, mbr, r):
      self.mbr = mbr
      self.r   = pointer
  def __str__(self):
      return "[RadialMbr]{ mbr: " + str(self.mbr) + ", r: " + str(self.r) + "}"
  def getMin(self,d):
    return self.mbr.getMin(d)
  def getMax(self,d):
    return self.mbr.getMax(d)
  def getR(self):
    return self.r
  def getMbr(self):
    return self.mbr
  def setRange(self, o):
    self.mbr.setRange(o)
    return self
  def distanceTo(self, mbrObject):
    return self.getMbr().distanceTo(mbrObject.getMbr())
  def returnExpandedMBR(self, mbrObject):
    return self.getMbr().returnExpandedMBR(mbrObject.getMbr())
  def getArea(self):
    return self.getMbr().getArea()
  def deadSpace(self, mbrObject):
    return self.getMbr().deadSpace(mbrObject.getMbr())
  def areIntersecting(self,mbrObject):
    return self.getMbr().areIntersecting(mbrObject.getMbr())