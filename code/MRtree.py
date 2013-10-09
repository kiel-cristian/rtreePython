from Mbr import *

class MbrPointer():
  def __init__(self, mbr, pointer):
    self.mbr     = mbr
    self.pointer = pointer

# COMPACTED OBJECTS
class MRtree(object):
    def __init__(self, d, M, offset, mbrs, pointers):
        self.d = d
        self.M = M
        self.offset = offset
        self.root = False

        self.pointers       = [p for p in pointers if p != -1]
        self.elems          = len(pointers)
        self.mbr            = Mbr(d)

        self.mbrs           = [m for m in mbrs if m != -2]
        
        # el Mbr del nodo, es el primer mbr de la lista, los demas corresponden a los de los hijos
        self.mbr.setRange(self.mbrs[0:self.d*2])

        childMbrsList = self.mbrs[self.d*2:]

        groupedList   = listToRanges(d, len(childMbrsList), childMbrsList)

        childMbrs     = [Mbr(d).setRange(g) for g in groupedList]

        self.mbrPointers = [MbrPointer(childMbrs[i], self.pointers[i]) for i in range(self.elems)]

    # Recibe un mbrPointer, y actualizo las estructuras internas
    def insert(self, mbrPointer):
        self.pointers[self.elems] = mbrPointer.pointer
        self.elems = self.elems + 1
        self.mbr.expand(mbrPointer.mbr)
        self.mbrs  = self.mbrs + mbrPointer.mbr.dump()
        self.mbrsPointers = self.mbrsPointers + [mbrPointer]

    def dumpMbrs(self):
        return self.mbrs     + [-2.0 for _ in range((self.M - self.elems )*2*self.d)]

    def dumpPointers(self):
        return self.pointers + [-1 for _ in range(self.M - self.elems)]

    def setAsRoot(self):
        self.root = True

    def printRtree(self):
        print "\tM: " + str(self.M)
        print "\toffset: " + str(self.offset)
        print "\td: " + str(self.d)
        print "\tmbr[" + str(self.mbr.len()) + "]: " + self.mbr.toStr()
        print "\tmbrs[" + str(len(self.mbrs)) + "]: " + str(self.mbrs)
        print "\tpointers[" + str(len(self.pointers)) + "]: " + str(self.pointers)

    def isANode(self):
        pass

    def isALeaf(self):
        pass

class MNode(MRtree):
    def __init__(self, M, d, offset, mbrs = [], pointers = []):
        super(MNode,  self).__init__(d = d, M = M, offset = offset, mbrs = mbrs, pointers = pointers)

    def printRtree(self):
        print "Node:"
        super(MNode, self).printRtree()

    def isANode(self):
        return True

    def isALeaf(self):
        return False

class MLeaf(MRtree):
    def __init__(self, M, d, offset, mbrs = [], pointers = []):
        super(MLeaf,  self).__init__(d = d, M = M, offset = offset, mbrs = mbrs, pointers = pointers)

    def printRtree(self):
        print "Leaf:"
        super(MLeaf, self).printRtree()

    def isANode(self):
        return False

    def isATree(self):
        return True

if __name__=="__main__":
    node = MNode(M = 20, d = 2, offset = 10, mbrs = [0.1, 0.1, 0.2, 0.2]*4,  pointers = [500, 100, 50])
    leaf = MLeaf(M = 8, d = 2, offset = 10, mbrs = [0.1, 0.1, 0.2, 0.2]*4, pointers = [100, 200, 300])

    node.printRtree()
    print "dumpMbr\t\t\t[" + str(len(node.dumpMbrs())) + "]: " + str(node.dumpMbrs())
    print "dumpPointer\t[" + str(len(node.dumpPointers())) + "]: " + str(node.dumpPointers())

    leaf.printRtree()
    print "dumpMbr\t\t\t[" + str(len(leaf.dumpMbrs())) + "]: " + str(leaf.dumpMbrs())
    print "dumpPointer\t[" + str(len(leaf.dumpPointers())) + "]: " + str(leaf.dumpPointers())

    node2 = MNode(M = 1, d = 2, offset = 10,  mbrs = [0.1, 0.1, 0.2, 0.2],  pointers = [])
    node2.printRtree()
    print "dumpMbr\t\t\t[" + str(len(node2.dumpMbrs())) + "]: " + str(node2.dumpMbrs())
    print "dumpPointer\t[" + str(len(node2.dumpPointers())) + "]: " + str(node2.dumpPointers())