from Mbr import *

# COMPACTED OBJECTS
class MRtree(object):
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

class MNode(MRtree):
    def __init__(self, maxE, d, offset, mbrList = [], pointers = []):
        super(MNode,  self).__init__(d = d, maxE = maxE, offset = offset)

        self.pointers       = [p for p in pointers if p != -1]
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
        return self.pointers + [-1 for _ in range(self.elemsM - self.elems)]

    def checkExpand(self, mbr):
        return self.mbr.checkExpand(mbr) and self.elems +1 < self.elemsM

    def printRtree(self):
        print "Node:"
        print "\telemsM: " + str(self.elemsM)
        print "\toffset: " + str(self.offset)
        print "\tmbr[" + str(self.mbr.len()) + "]: " + self.mbr.toStr()
        print "\tpointers[" + str(len(self.pointers)) + "]: " + str(self.pointers)

class MLeaf(MRtree):
    def __init__(self, maxE, d, offset, vectorList):
        super(MLeaf,  self).__init__(d = d, maxE = maxE/2, offset = offset)
        vector = []
        self.vectors = []
        k = 0
        for i in range(len(vectorList)):
            v = vectorList[i]
            vector = vector + [v]
            k = k + 1

            if k >= d:
                vector = [v for v in vector if v != -2]
                if len(vector) == d:
                    self.vectors = self.vectors + [vector]
                vector = []
                k = 0

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
        return [val for subl in self.vectors for val in subl] + 2*[-2 for _ in range(self.elemsM - self.elems)]

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
    node = MNode(maxE = 20, d = 2, offset = 10,  mbrList = [0.1, 0.1, 0.2, 0.2],  pointers = [1, 500, 1000])
    leaf = MLeaf(maxE = 8, d = 2, offset = 10, vectorList = [1.0,2.5])

    node.printRtree()
    print "dumpMbr\t\t\t[" + str(len(node.dumpMbr())) + "]: " + str(node.dumpMbr())
    print "dumpPointer\t[" + str(len(node.dumpPointers())) + "]: " + str(node.dumpPointers())

    leaf.printRtree()
    print "dump\t[" + str(len(leaf.dump())) + "]: " + str(leaf.dump())

    node2 = MNode(maxE = 1, d = 2, offset = 10,  mbrList = [0.1, 0.1, 0.2, 0.2],  pointers = [])
    node2.printRtree()
    print "dumpMbr\t\t\t[" + str(len(node2.dumpMbr())) + "]: " + str(node2.dumpMbr())
    print "dumpPointer\t[" + str(len(node2.dumpPointers())) + "]: " + str(node2.dumpPointers())