class Mbr:
    def __init__(self, d, minV = 0, maxV = 1):
        self.d          = d
        self.coords     = [maxV,minV]*self.d
        self.dRanges    = self.listToRange(d, self.coords)

    def listToRange(self, d, coords):
        dRanges = []
        for k in range(0, d, 1):
            dimensionMin = coords[2*k]
            dimensionMax = coords[2*k+1]
            dRanges = dRanges + [[dimensionMin, dimensionMax]]
        return dRanges

    def setRange(self, dataList):
        if len(dataList) != self.d*2:
            raise "Error on dataList length"

        self.coords  = dataList
        self.dRanges = self.listToRange(self.d, dataList)

    def setPoint(self, dPoint):
        if len(dPoint) != self.d:
            raise "Error on point dimension"

        dup = [[x,x] for x in dPoint]
        self.coords = [val for subl in dup for val in subl]
        self.dRanges = self.listToRange(self.d, self.coords)

    def checkExpand(self, mbr):
        diffs = {}
        for i in range(self.d):
            r = self.dRanges[i]
            dMin = r[0]
            dMax = r[1]

            if mbr.dRanges[i][0] < dMin:
                diffs[i] = dMin - mbr.dRanges[i][0]
            elif mbr.dRanges[i][1] > dMax:
                diffs[i] = dMax - mbr.dRanges[i][1]

        a = 1
        for k in diffs:
            a = a*k

        if a > 1:
            return a
        else:
            return 0

    def expand(self, mbr):
        for i in range(self.d):
            r = self.dRanges[i]
            dMin = r[0]
            dMax = r[1]

            if mbr.dRanges[i][0] < dMin:
                diffs[i] = dMin - mbr.dRanges[i][0]
                self.coords[2*i] = mbr.coords[2*i]
            elif mbr.dRanges[i][1] > dMax:
                self.dRanges[i][1] = mbr.dRanges[i][1]
                self.coords[2*i+1] = mbr.coords[2*i+1]

if __name__=="__main__":
    m = Mbr(2)
    if not m.dRanges == [[1,0], [1,0]]:
        raise "Error on dRanges"
    if not m.coords  == [1,0,1,0]:
        raise "Error on coords"

    m.setRange([0.5, 0.568, 0.1, 0.2])

    if not m.dRanges == [[0.5, 0.568], [0.1, 0.2]]:
        raise "Error on dRanges"
    if not m.coords  == [0.5, 0.568, 0.1, 0.2]:
        raise "Error on coords"

    m.setPoint([0.2, 0.7])
    if not m.dRanges == [[0.2, 0.2],[0.7, 0.7]]:
        raise "Error on dRanges"
    if not m.coords == [0.2, 0.2, 0.7, 0.7]:
        raise "Error on coords"