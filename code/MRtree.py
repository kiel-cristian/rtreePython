# encoding: utf-8
from Mbr import *
from MbrPointer import *
from RadialMbr import *
from time import time

class MRtreeLoadError(Exception):
    def __init__(self):
        self.value = "Largo del MBR debe coincidir con el de punteros"
    def __str__(self):
        return repr(self.value)

class MRtreeAddChildError(Exception):
    def __init__(self, value = "Tipos a insertar incorrectos"):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MRtreeUpdateChildError(Exception):
    def __init__(self):
        self.value = "Error actualizando hijo, no encontrado"
    def __str__(self):
        return repr(self.value)

# MEMORY OBJECTS
class MRtree(object):
    def __init__(self, d, M, offset = 0, mbrs = [], pointers = []):
        self.d = d
        self.M = M
        self.offset = offset
        self.root = False

        self.mbrs           = [m for m in mbrs if m != -2.0]
        self.pointers       = [p for p in pointers if p != -1]

        self.elems          = len(self.pointers)
        self.mbr            = Mbr(d)
        
        childMbrsList = self.mbrs[:]
        groupedList   = listToRanges(d, len(childMbrsList), childMbrsList)
        childMbrs     = [Mbr(d).setRange(g) for g in groupedList]

        if self.elems != len(groupedList):
            raise MRtreeLoadError()

        # Se calcula el mbr del Nodo actual, en base a los mbrs de los hijos
        for m in childMbrs:
            self.mbr.expand(m)

        # Mbrs
        self.childMbrs = childMbrs

        # Tuplas de (mbr, punteros) hijos
        self.mbrPointers = [MbrPointer(childMbrs[i], self.pointers[i]) for i in range(self.elems)]

    def __str__(self):
        return "[Tree]{ p:" + str(self.offset) + ", mbr: " + str(self.mbr) + ", childs: " + str([str(_) for _ in self.mbrPointers]) + "}"

    # Setea la info proveniendo de un split dentro del nodo u hoja
    def setSplitData(self, thisNodeMbr, childrenMbrPointers):
        pass

    # Añade un hijo al arbol actual (Una tupla (mbr, pointer))
    def insert(self, mbrPointer):
        pointer = mbrPointer.getPointer()
        mbr     = mbrPointer.getMbr()

        self.pointers = self.pointers + [pointer]
        self.elems = self.elems + 1
        self.mbr.expand(mbr)
        self.mbrs  = self.mbrs + mbr.dump()
        self.mbrPointers = self.mbrPointers + [MbrPointer(mbr, pointer)]

    # Actualiza un hijo en base a puntero, y, actualiza el mbr del arbol
    def updateChild(self, mbrPointer):
        change = False
        for i in range(self.elems):
            m = self.mbrPointers[i]

            if m.getPointer() == mbrPointer.getPointer():
                self.mbrPointers[i] = mbrPointer
                change = True
                break

        if not change:
            raise MRtreeUpdateChildError()
        self.mbr.expand(mbrPointer.getMbr())

    def getPointer(self):
        return self.offset

    def setPointer(self, p):
        self.offset = p

    # Esta estructura se ocupa para algoritmos del Rtree
    def getChildren(self):
        return self.mbrPointers

    def getChildrenMbrs(self):
        return self.childMbrs

    def getMbr(self):
        return self.mbr

    # Esta estructura se ocupa para insertar una version compacta del Nodo a otro Nodo u Hoja
    def getMbrPointer(self):
        return MbrPointer(self.mbr, self.offset)

    def dumpMbrs(self):
        return self.mbrs     + [-2.0 for _ in range((self.M - self.elems )*2*self.d)]

    def dumpPointers(self):
        return self.pointers + [-1 for _ in range(self.M - self.elems)]

    def setAsRoot(self, rootOffset = 0):
        self.root   = True
        self.offset = rootOffset

    def unsetRoot(self):
        self.root = False

    def needToSplit(self):
        return self.elems == self.M

    def isANode(self):
        pass

    def isALeaf(self):
        pass

class MNode(MRtree):
    def __init__(self, M, d, offset = -1, mbrs = [], pointers = []):
        super(MNode,  self).__init__(d = d, M = M, offset = offset, mbrs = mbrs, pointers = pointers)
        self.partitionCount = 0

    def __str__(self):
        return "[Node]{ p:" + str(self.offset) + ", mbr: " + str(self.mbr) + ", childs: " + str([str(_) for _ in self.mbrPointers]) + "}"

    def isANode(self):
        return True

    def isALeaf(self):
        return False

class MLeaf(MRtree):
    def __init__(self, M, d, offset = -1, mbrs = [], pointers = []):
        super(MLeaf,  self).__init__(d = d, M = M, offset = offset, mbrs = mbrs, pointers = pointers)

    def __str__(self):
        return "[Leaf]{ p:" + str(self.offset) + ", mbr: " + str(self.mbr) + ", childs: " + str([str(_) for _ in self.mbrPointers]) + "}"

    def isANode(self):
        return False

    def isALeaf(self):
        return True

if __name__=="__main__":
    node = MNode(M = 20, d = 2, offset = 10, mbrs = [0.1, 0.1, 0.2, 0.2]*3,  pointers = [500, 100, 50])
    leaf = MLeaf(M = 8, d = 2, offset = 10, mbrs = [0.1, 0.1, 0.2, 0.2]*3, pointers = [100, 200, 300])

    print(str(node))
    print("dumpMbr\t\t\t[" + str(len(node.dumpMbrs())) + "]: " + str(node.dumpMbrs()))
    print("dumpPointer\t[" + str(len(node.dumpPointers())) + "]: " + str(node.dumpPointers()))

    print(str(leaf))
    print("dumpMbr\t\t\t[" + str(len(leaf.dumpMbrs())) + "]: " + str(leaf.dumpMbrs()))
    print("dumpPointer\t[" + str(len(leaf.dumpPointers())) + "]: " + str(leaf.dumpPointers()))

    node2 = MNode(M = 1, d = 2, offset = 10,  mbrs = [0.1, 0.1, 0.2, 0.2],  pointers = [1])
    print(str(node2))
    print("dumpMbr\t\t\t[" + str(len(node2.dumpMbrs())) + "]: " + str(node2.dumpMbrs()))
    print("dumpPointer\t[" + str(len(node2.dumpPointers())) + "]: " + str(node2.dumpPointers()))

    # Simboliza raiz vacia
    root  = MNode(M = 50, d = 2, offset = 0,  mbrs = [],  pointers = [])
    print(str(root))

    leaf2 = MLeaf(M=2, d = 2, offset = 0, mbrs = [0.2, 0.3, 0.2, 0.3]*2, pointers = [1, 20])
    print(str(leaf2))

    mbrPointer = MbrPointer(Mbr(2).setRange([0.2,0.3,0.2,0.5]), 20)
    mbrPointer.pointer = 20

    leaf2.updateChild(mbrPointer)
    print(str(leaf2))