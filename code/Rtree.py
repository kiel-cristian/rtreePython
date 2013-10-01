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
    # d : Tree object entries dimensions
    # n : Maximun object entries
    def __init__(self, d, blockBytes = 4096, maxE = 100000):
        nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
                                dataFile        = "rtree" + str(d) + "D.bin",
                                d               = d,
                                blockBytes      = blockBytes)

        self.nfh = nfh
        self.cache = []                             # cache:      Rtree node cache
        self.k = 0                                  # k:          Nodes on cache
        self.maxK = log(maxE, self.M()) -1            # maxK:      Max nodes on cache

        # Init Rtree
        root = MNode(maxE = self.nfh.p, d = d, offset = 0, mbrList = Mbr(d).dump(), pointers = [])
        root.setAsRoot()
        self.currentNode = root
        self.root     = True
        self.nfh.addTree(self.currentNode)

    # Minimun node entries
    def m(self):
        return self.nfh.m

    # Maximun node entries
    def M(self):
        return self.nfh.M

    def needToSplit(self):
        return self.elems + 1 > self.M

    def isNode(self, p):
        return self.nfh.isNode(p)

    def newLeaf(self):
        return

    def newNode(self):
        return EmptyNode(maxE = self.nfh.p, d = d, offset = 0, mbrLen = self.nfh.r, pointersLen = self.nfh.p)

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
        checkPointer = self.pointers[0]

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
    rtree = Rtree(d)
    rtree.loadRtreeData()