from Mbr import *

# COMPACTED OBJECTS
class CompactRtree(object):
    def __init__(self, d, maxE, offset):
        self.maxElems = maxE
        self.offset = offset
        self.d = d
        self.root = False
        self.elems = 0
    def fillEmptyElements(self):
        pass
    def printRtree(self):
        pass
    def insert(self,data):
        pass
    def setAsRoot(self):
        self.root = True

class CompactNode(CompactRtree):
    def __init__(self, maxE, d, offset, mbr = [], pointers = []):
        super(CompactNode,  self).__init__(d = d, maxE = maxE, offset = offset)
        self.pointers       = pointers
        mbr                 = Mbr(d)
        mbr.setRange(mbr) if mbr
        self.innerMbr       = mbr
        self.__fillEmptyElements()

    def mbr(self):
        self.innerMbr.coords

    def checkExpand(self, mbr):
        return self.mbr.checkExpand(mbr)

    def addNode(self, mbr, pointer):
        self.pointers[self.elems] = pointer
        self.elems = self.elems + 1
        self.innerMbr.expand(mbr)

    def __fillEmptyElements(self):
        self.mbr = [-2.0 for _ in range(self.mbrLen)]
        self.pointers = [-1 for _ in range(self.pointersLen)]

    def getMbr(self):
        return self.mbr.coords

    def printRtree(self):
        print "Node:"
        print "\tmaxElems: " + str(self.maxElems)
        print "\toffset: " + str(self.offset)
        print "\tmbr[" + str(len(self.mbr)) + "]: " + str(self.mbr)
        print "\tpointers[" + str(len(self.pointers)) + "]: " + str(self.pointers)

class CompactLeaf(CompactRtree):
    def __init__(self, maxE, d, offset, vectorsLen):
        super(CompactLeaf,  self).__init__(d = d, maxE = maxE, offset = offset)
        self.vectors = vectors
        self.d = d
        self.fillEmptyElements()

    def set(self, vectors):
        vectors

    def fillEmptyElements(self):
        diffElems = self.maxElems - len(self.vectors)
        if  diffElems > 0:
            self.vectors = self.vectors + [-2.0 for _ in range(diffElems)]

    def printRtree(self):
        print "Leaf:"
        print "\tmaxElems: " + str(self.maxElems)
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
    node = CompactNode(maxE = 20, d = 2, offset = 10,  mbr = [1.0, 3.0],  pointers = [1, 500, 1000])
    leaf = CompactLeaf(maxE = 8, d = 2, offset = 10, vectors = [1.0,2.5])
    node.printRtree()
    leaf.printRtree()

    emptyNode = EmptyNode(maxE = 10, d = 2, offset = 10, mbrLen = 2, pointersLen = 100)
    emptyNode.printRtree()
    emptyLeaf = EmptyLeaf(maxE = 8, d = 2, offset = 10, vectorsLen = 2)
    emptyLeaf.printRtree()

    print node.getMbr()
    print leaf.getVectors()