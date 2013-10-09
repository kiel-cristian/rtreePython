from math import log
import sys
import struct
from FileHandler import *
from MRtree import *

#  ERRORS
class RtreeHeightError(Exception):
    def __init__(self):
        self.value = "height error"
    def __str__(self):
        return repr(self.value)

class Rtree(object):
    # d          : dimension de vectores del arbol
    # M          : capacidad maxima de nodos y hojas
    # maxE       : cantidad maxima de elementos que almacenara el Rtree
    # reset      : cuando es True, se construye un nuevo arbol, si no, se carga de disco
    # initOffset : offset desde se cargara nodo raiz
    def __init__(self, d, M = 100, maxE = 100000, reset = False, initOffset = 0):
        self.nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
                                dataFile        = "rtree" + str(d) + "D.bin",
                                d               = d,
                                M               = M)

        self.cache = []                             # cache: lista de nodos visitados
        self.k = 0                                  # k: nodos en cache
        self.H = log(maxE, self.M()) -1             # H: altura maxima del arbol

        # Inicializacion de la raiz
        if reset:
            # Se construye una raiz vacia
            self.currentNode = self.newNode(initOffset)
            self.currentNode.setAsRoot()

            # Creo dos hojas para mantener invariante de la raiz
            leaf1 = self.newLeaf(initOffset)
            leaf2 = self.newLeaf(initOffset)

            # Guardo dos hojas de la raiz en disco
            self.nfh.saveTree(leaf1)
            self.nfh.saveTree(leaf2)

            # Agrego las hojas al nodo raiz
            self.currentNode.insert(leaf1)
            self.currentNode.insert(leaf2)

            # Guardo el nodo raiz en disco
            self.nfh.saveTree(self.currentNode)

            # Guardo una referencia al nodo raiz
            self.root = self.currentNode
        else:
            # se carga la raiz de disco
            self.currentNode = self.nfh.readTree(initOffset)
            self.currentNode.setAsRoot()
            self.root = self.currentNode

    # Capacidad minima de nodos y hojas
    def m(self):
        return self.nfh.m

    # Capacidad maxima de nodos y hojas
    def M(self):
        return self.nfh.M

    def d(self):
        return self.nfh.d

    def needToSplit(self):
        return self.elems + 1 > self.M

    def isNode(self, p):
        return self.nfh.isNode(p)

    def newLeaf(self, initOffset):
        return MLeaf(M = self.M(), d = self.d(), offset = initOffset, mbrs = [], pointers = [])

    def newNode(self, initOffset):
        return MNode(M = self.M(), d = self.d(), offset = initOffset, mbrs = [], pointers = [])

    def loadRtreeData(self):
        vectors = self.nfh.getVectors()
        for v in vectors:
            self.insert(v)

    def seekNode(self, pointer):
        if self.k < self.maxK:
            # Can load another node to cache
            self.k = self.k + 1

            # save previous data to cache
            self.cache = [self.mNode] + self.cache

            # Load Node data from disk
            mNode = self.nfh.readTree(pointer)

            self.mbr      = mNode.getMbr()
            self.pointers = mNode.pointers
            self.elems    = mNode.getElems()
            self.root     = mNode.root
        else:
            raise RtreeHeightError()

    def insert(self, vector):
        checkPointer = self.currentNode.pointers[0]

        if self.isNode(checkPointer):
            p = self.chooseTree(vector)
            self.seekNode(p)
            self.insert(vector)

        else:
            if self.needToSplit:
                node = self.cache[0]
                newNode = EmptyNode()
                parent = self.cache[1]

                self.splitNode(parent,node,newNode)
                self.adjustTree()
            else:
                mLeaf = self.chooseLeaf(vector)
                self.nfh.writeTree(mLeaf)

                currentNode = self.cache[0]
                currentNode.adjustMbr(mLeaf)

                self.nfh.writeTree(currentNode)
                self.adjustTree()
                return

    def chooseLeaf(self,vector):
        l = self.chooseTree(vector)
        if l == -1:
            return EmptyLeaf()
        else:
            return self.readTree(l)

    def chooseTree(self, vector):
        minPointer = self.pointers[0]
        minIncrement = 0

        for p in self.pointers:
            leafMbr = self.nfh.getMbr(p)
            increment = self.getIncrement(leafMbr, vector)
            if increment < minIncrement:
                minPointer = p
                minIncrement = increment
        return minPointer

    def splitNode(self,parent,mNode, newNode):
        pass

    def adjustTree(self):
        for i in range(0,self.cache-1):
            modifiedNode = self.cache[i]
            needToModify = self.cache[i+1]
            needToModify.adjustMbr(modifiedNode)
            self.nfh.writeTree(needToModify)

        # for node in self.cache:
        #     newMbr = [[0.0,0.0] for _ in range(self.d)]
        #     for p in node.pointers:
        #         childMbr = self.nfh.getMbr(p)
        #         for i in range(0,self.d):
        #             coords = childMbr[i]
        #             if coords[0] < newMbr[i][0]:
        #                 newMbr[i][0] = coords[0]
        #             if coords[1] > newMbr[i][1]:
        #                 newMbr[i][1] = coords[1]

        #     mMbr = []
        #     for coords in newMbr:
        #         mMbr = mMbr + coords[0] + coords[1]
        #     node.mbr = mMbr
        #     self.nfh.writeTree(node)

    def rangeQuery(self, q, epsilon, node):
        pass

    def minDist(self, q, region):
        pass

if __name__=="__main__":
    d = 2
    M = 100
    rtree = Rtree(d = d, M = 100, maxE = 10**6, reset = True)
    # rtree.loadRtreeData()