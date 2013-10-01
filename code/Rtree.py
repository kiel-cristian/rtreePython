from math import log
import sys
import struct
from FileHandler import *
from CompactRtree import *

NodeBytes = 4096 # Bytes per node

#  ERRORS
class RtreeHeightError(Exception):
    def __init__(self):
        self.value = "height error"
    def __str__(self):
        return repr(self.value)

class Rtree(object):
    # d : Tree object entries dimensions
    # n : Maximun object entries
    def __init__(self, d, n = 100000):
        bBytes     = NodeBytes
        idBytes    = struct.calcsize("?")
        rBytes     = 2*d*struct.calcsize("d")
        pBytes     = bBytes - idBytes - rBytes
        vBytes     = bBytes - idBytes

        # adjustment
        pBytes = pBytes - pBytes % struct.calcsize("i")
        vBytes = vBytes - vBytes % struct.calcsize("d")

        nBytes = rBytes + pBytes + idBytes
        lBytes = idBytes + vBytes

        nfh = RtreeFileHandler( dataFile = "rtree" + str(d) + "D.bin",
                                d = d,
                                blockBytes = bBytes,
                                nodeBytes = nBytes,
                                leafBytes = lBytes,
                                idBytes = idBytes,
                                rBytes = rBytes,
                                pBytes = pBytes,
                                vBytes = vBytes)

        self.nfh = nfh
        self.M = pBytes/struct.calcsize("i")       # M:          Maximum node entries
        self.m = self.M/2                           # m:          Minimun node entries
        self.cache = []                             # cache:      Rtree node cache
        self.k = 0                                  # k:          Nodes on cache
        self.maxK = log(n, self.M) -1              # maxK:      Max nodes on cache
        self.dataFile = "data" + str(d) + "D.bin"  # dataFile:  Data for loading vectors

        # Init Rtree
        root = CompactNode(maxE = self.nfh.p, d = d, offset = 0, mbrLen = self.nfh.r, pointersLen = self.nfh.p)
        root.setAsRoot()
        self.currentNode = root
        self.root     = True
        self.nfh.addTree(self.currentNode)

    def needToSplit(self):
        return self.elems + 1 > self.M

    def isNode(self, p):
        return self.nfh.isNode(p)

    def newLeaf(self):
        return

    def newNode(self):
        return EmptyNode(maxE = self.nfh.p, d = d, offset = 0, mbrLen = self.nfh.r, pointersLen = self.nfh.p)

    def loadRtreeData(self):
        vectors = self.nfh.getVectors(self.dataFile)
        for v in vectors:
            self.insert(v)

    def seekNode(self, pointer):
        if self.k < self.maxK:
            # Can load another node to cache
            self.k = self.k + 1

            # save previous data to cache
            self.cache = [self.compactNode] + self.cache

            # Load Node data from disk
            compactNode = self.nfh.readTree(pointer)

            self.mbr      = compactNode.getMbr()
            self.pointers = compactNode.pointers
            self.elems    = compactNode.getElems()
            self.root     = compactNode.root
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
                compactLeaf = self.chooseLeaf(vector)
                self.nfh.writeTree(compactLeaf)

                currentNode = self.cache[0]
                currentNode.adjustMbr(compactLeaf)

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

    def splitNode(self,parent,compactNode, newNode):
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

        #     compactMbr = []
        #     for coords in newMbr:
        #         compactMbr = compactMbr + coords[0] + coords[1]
        #     node.mbr = compactMbr
        #     self.nfh.writeTree(node)

    def rangeQuery(self, q, epsilon, node):
        pass

    def minDist(self, q, region):
        pass

if __name__=="__main__":
    d = 2
    rtree = Rtree(d)
    rtree.loadRtreeData()