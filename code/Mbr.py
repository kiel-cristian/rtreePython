from MbrApi import *
from math import sqrt

class Mbr(MbrApi):
    def __init__(self, d, minV=0, maxV=1):
        super(Mbr, self).__init__()
        self.d = d
        self.coords = [maxV, minV] * self.d
        self.dRanges = self.listToRange(self.coords)

    def __str__(self):
        return "Mbr:" + str(self.dRanges)

    def cutOnDimension(self, dToCut, cut):
        dumpCopy = self.dump()[:]
        firstCopy    = Mbr(self.d).setRange(dumpCopy)
        secondCopy = Mbr(self.d).setRange(dumpCopy)

        for i in range(self.d):
            if i == dToCut:
                firstCopy.setMax(i, cut)
                secondCopy.setMin(i, cut)
        return [firstCopy, secondCopy]

    def getCenter(self):
        mid = []
        for d in range(self.d):
            mid = mid + [(self.getMin(d) + self.getMax(d))/2]
        return mid

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

            if mbr.getMin(i) < dMin or dMin == 1:
                self.setMin(i, mbr.getMin(i))

            if mbr.getMax(i) > dMax or dMax == 0:
                self.setMax(i, mbr.getMax(i))
        return self

    def areIntersecting(self,mbr):
        for d in range(self.d):
            mMin = self.getMin(d)
            mMax = self.getMax(d)
            eMin = mbr.getMin(d)
            eMax = mbr.getMax(d)
            if(not((eMin >= mMin and eMin <= mMax) or (eMax >= mMin and eMax <= mMax))):
                return False
        return True

def listToRanges(d, n, coords):
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

if __name__ == "__main__":
    m = Mbr(2)
    if not m.dRanges == [[1, 0], [1, 0]]:
        print("Error on dRanges")
    if not m.coords == [1, 0, 1, 0]:
        print("Error on coords")

    m.setRange([0.5, 0.568, 0.1, 0.2])

    if not m.dRanges == [[0.5, 0.568], [0.1, 0.2]]:
        print("Error on dRanges")
    if not m.coords == [0.5, 0.568, 0.1, 0.2]:
        print("Error on coords")

    m.setPoint([0.2, 0.7])
    if not m.dRanges == [[0.2, 0.2], [0.7, 0.7]]:
        print("Error on dRanges")
    if not m.coords == [0.2, 0.2, 0.7, 0.7]:
        print("Error on coords")


    m2 = Mbr(2)
    m2.setPoint([0.3, 0.7])

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

    m3 = Mbr(2)
    print(m3.dump())
    cuts = m3.cutOnDimension(0,0.25)
    print(cuts[0])
    print(cuts[1])
    print(m3.dump())