import random
from math import sqrt

class MbrError(Exception):
    def __init__(self):
        self.value = "mbr error"
    def __str__(self):
        return repr(self.value)
class MbrDataListLengthError(MbrError):
    pass
class MbrPointDimensionError(MbrError):
    pass

class MbrApi():
  def getMin(self,d):
    pass
  def getMax(self,d):
    pass
  def distanceTo(self, o):
    pass
  def returnExpandedMBR(self, o):
    pass
  def getArea(self):
    pass
  def deadSpace(self, o):
    pass

class MbrPointer(MbrApi):
  def __init__(self, mbr, pointer):
      self.mbr     = mbr
      self.pointer = pointer
  def __str__(self):
      return "{mbr: " + str(self.mbr) + ", p: " + str(self.pointer) + "}"
  def getMin(self,d):
    return self.mbr.getMin(d)
  def getMax(self,d):
    return self.mbr.getMax(d)
  def getPointer(self):
    return self.pointer
  def getMbr(self):
    return self.mbr
  def distanceTo(self, mbrPointer):
    return self.getMbr().distanceTo(mbrPointer.getMbr())
  def returnExpandedMBR(self, mbrPointer):
    return self.getMbr().returnExpandedMBR(mbrPointer.getMbr())
  def getArea(self):
    return self.getMbr().getArea()
  def deadSpace(self, mbrPointer):
    return self.getMbr().deadSpace(mbrPointer.getMbr())

class Mbr(MbrApi):
    def __init__(self, d, minV=0, maxV=1):
        self.d = d
        self.coords = [maxV, minV] * self.d
        self.dRanges = self.listToRange(self.coords)
        
    def __str__(self):
        return str(self.dRanges)

    def getArea(self):
      area = -1.0
      for d in range(0, self.d):
        if area == -1.0:
          area = self.getMax(d) - self.getMin(d)
        else:
          area = area * (self.getMax(d) - self.getMin(d))
      return area

    def getMin(self, dimension):
        return self.dRanges[dimension][0]

    def setMin(self, dimension, newMin):
        self.dRanges[dimension][0] = newMin
        self.coords[2 * dimension] = newMin

    def getMax(self, dimension):
        return self.dRanges[dimension][1]

    def setMax(self, dimension, newMax):
        self.dRanges[dimension][1] = newMax
        self.coords[2 * dimension + 1] = newMax

    # Calcula la distancia a otro mbr usando rangos inferiores en cada dimension
    # mbr : Otro mbr
    def distanceTo(self, mbr):
        distance = 0
        for i in range(self.d):
            distance = distance + (mbr.getMin(i) - self.getMin(i)) ** 2
        return sqrt(distance)

    def listToRange(self, coords):
        dRanges = []
        for k in range(0, self.d, 1):
            dimensionMin = coords[2 * k]
            dimensionMax = coords[2 * k + 1]
            dRanges = dRanges + [[dimensionMin, dimensionMax]]
        return dRanges

    def equals(self, mbr):
        for d in range(self.d):
            if self.getMin(d) != mbr.getMin(d) or self.getMax(d) != mbr.getMax(d):
                return False
        return True

    def len(self):
        return self.d * 2

    def dump(self):
        return self.coords

    def setRange(self, dataList):
        if len(dataList) != self.len():
            raise MbrDataListLengthError()

        self.coords = dataList
        self.dRanges = self.listToRange(dataList)
        return self

    def setPoint(self, dPoint):
        if len(dPoint) != self.d:
            raise MbrPointDimensionError()

        dup = [[x, x] for x in dPoint]
        self.coords = [val for subl in dup for val in subl]
        self.dRanges = self.listToRange(self.coords)
        return self

    # Retorna el espacio muerto resultante de unir 2 MBR's
    def deadSpace(self, mbr):
      return self.returnExpandedMBR(mbr).getArea() - (self.getArea() + mbr.getArea())

    def checkExpand(self, mbr):
        a = 1
        diff = 0
        for i in range(self.d):
            dMin = self.getMin(i)
            dMax = self.getMax(i)

            if mbr.getMin(i) < dMin:
                diff = dMin - mbr.getMin(i)

            if mbr.getMax(i) > dMax:
                diff = diff + (dMax - mbr.getMax(i))

            a = a * diff

        if a > 0 or not self.equals(mbr):
            return [True, a]
        else:
            return [False, 0]
          
    # Retorna un MBR que incluya el actual y el mbr dado      
    def returnExpandedMBR(self, mbr):
      expandedMbr = Mbr(self.d)
      for i in range(self.d):
        dMin = self.getMin(i)
        dMax = self.getMax(i)
        if mbr.getMin(i) < dMin:
          expandedMbr.setMin(i, mbr.getMin(i))
        else:
          expandedMbr.setMin(i, dMin)
        if mbr.getMax(i) > dMax:
          expandedMbr.setMax(i, mbr.getMax(i))
        else:
          expandedMbr.setMax(i, dMax)
      return expandedMbr
    
    # Expande el MBR actual para que incluya tambien el mbr dado
    def expand(self, mbr):
        for i in range(self.d):
            dMin = self.getMin(i)
            dMax = self.getMax(i)

            if mbr.getMin(i) < dMin:
                self.setMin(i, mbr.getMin(i))
                
            elif mbr.getMax(i) > dMax:
                self.setMax(i, mbr.getMax(i))

def listToRanges(d, n, coords):
    helper = Mbr(d)
    dRanges = []
    mbrCoords = []
    i = 0
    while i < n:
        for j in range(2 * d):
            mbrCoords = mbrCoords + [coords[i]]
            i = i + 1

        dRanges = dRanges + [mbrCoords]
        mbrCoords = []

    return dRanges

def randomMbrPointer(d):
  randomPoint = [random.random() for _ in range(d)]
  return Mbr(d).setPoint(randomPoint)

if __name__ == "__main__":
    m = Mbr(2)
    if not m.dRanges == [[1, 0], [1, 0]]:
        raise "Error on dRanges"
    if not m.coords == [1, 0, 1, 0]:
        raise "Error on coords"

    m.setRange([0.5, 0.568, 0.1, 0.2])

    if not m.dRanges == [[0.5, 0.568], [0.1, 0.2]]:
        raise "Error on dRanges"
    if not m.coords == [0.5, 0.568, 0.1, 0.2]:
        raise "Error on coords"

    m.setPoint([0.2, 0.7])
    if not m.dRanges == [[0.2, 0.2], [0.7, 0.7]]:
        raise "Error on dRanges"
    if not m.coords == [0.2, 0.2, 0.7, 0.7]:
        raise "Error on coords"


    m2 = Mbr(2)
    m2.setPoint([0.3, 0.7])
    print(m.checkExpand(m2))

    m.setPoint([0.3, 0.7])
    print(m.distanceTo(m2) == 0)
    print(m2.distanceTo(m) == 0)

    m.setPoint([0.4, 0.7])
    print(m.distanceTo(m2))

    m.setPoint([0.8, 1.4])
    print(m.distanceTo(m2))
    
    print(m.returnExpandedMBR(m2).dRanges)
    print(m.returnExpandedMBR(m2).getArea())
    print(m.getArea() + m2.getArea())

