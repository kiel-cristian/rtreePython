from Mbr import *

# COMPACTED OBJECTS
class CompactRtree(object):
    def __init__(self, d, maxE, offset):
        self.elemsM = maxE
        self.offset = offset
        self.d = d
        self.root = False
        self.elems = 0
    def printRtree(self):
        pass
    def insert(self,data):
        pass
    def dump(self):
        pass
    def setAsRoot(self):
        self.root = True

class CompactNode(CompactRtree):
    def __init__(self, maxE, d, offset, mbrList = [], pointers = []):
        super(CompactNode,  self).__init__(d = d, maxE = maxE, offset = offset)

        self.pointers       = pointers
        self.elems          = len(pointers)

        mbr                 = Mbr(d)
        if mbr:
            mbr.setRange(mbrList)
        self.mbr       = mbr

    # data : Arreglo que contiene el mbr y el puntero a disco
    def insert(self, data):
        self.addNode(data[0], data[1])

    def addNode(self, mbr, pointer):
        self.pointers[self.elems] = pointer
        self.elems = self.elems + 1
        self.mbr.expand(mbr)

    def dump(self):
        return self.dumpMbr() + self.dumpPointers()

    def dumpMbr(self):
        return self.mbr.dump()

    def dumpPointers(self):
        return self.pointers + [-1 for _ in range(self.elemsM - self.elems + 1)]

    def checkExpand(self, mbr):
        return self.mbr.checkExpand(mbr) and self.elems +1 < self.elemsM

    def printRtree(self):
        print "Node:"
        print "\telemsM: " + str(self.elemsM)
        print "\toffset: " + str(self.offset)
        print "\tmbr[" + str(self.mbr.len()) + "]: " + self.mbr.toStr()
        print "\tpointers[" + str(len(self.pointers)) + "]: " + str(self.pointers)

class CompactLeaf(CompactRtree):
    def __init__(self, maxE, d, offset, vectorList):
        super(CompactLeaf,  self).__init__(d = d, maxE = maxE, offset = offset)

        self.vectors = vectorList
        self.elems   = len(self.vectors)
        self.mbrs    = [Mbr(d) for _ in range(self.elems)]
        self.mbrs    = [self.mbrs[k].setPoint(self.vectors[k]) for k in range(self.elems)]

    # data: Punto kDimensional
    def insert(self, data):
        self.addLeaf(data)

    def addLeaf(self, point):
        self.vectors[self.elems] = point
        self.elems = self.elems + 1
        self.mbrs[self.elems] = Mbr(self.d)
        self.mbrs[self.elems] = self.mbrs[self.elems].setPoint(point)

    def dump(self):
        return [val for subl in self.vectors for val in subl] + [-2 for _ in range(self.elemsM - self.elems + 1)]

    def printRtree(self):
        print "Leaf:"
        print "\telemsM: " + str(self.elemsM)
        print "\toffset: " + str(self.offset)
        print "\td: " + str(self.d)
        print "\tvectors[" + str(len(self.vectors)) + "]: " + str(self.vectors)

    def getVectors(self):
        if self.vectors:
            i = 0
            mbr = []
            point = []
            l = len(self.vectors)
            while i < l:
                point = [self.vectors[i] ,self.vectors[i+1]]
                mbr = mbr + [point]
                i = i + self.d
            return mbr
        return []

if __name__=="__main__":
    node = CompactNode(maxE = 20, d = 2, offset = 10,  mbrList = [0.1, 0.1, 0.2, 0.2],  pointers = [1, 500, 1000])
    leaf = CompactLeaf(maxE = 8, d = 2, offset = 10, vectorList = [[1.0,2.5]])
    node.printRtree()
    leaf.printRtree()

    #emptyNode = EmptyNode(maxE = 10, d = 2, offset = 10, mbrLen = 2, pointersLen = 100)
    #emptyNode.printRtree()
    #emptyLeaf = EmptyLeaf(maxE = 8, d = 2, offset = 10, vectorsLen = 2)
    #emptyLeaf.printRtree()

    print node.dump()
    print leaf.dump()