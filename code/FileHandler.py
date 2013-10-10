# encoding: utf-8
import io
import random
import struct
import sys

from MRtree import *


# ERRORS
class FileHandlerError(Exception):
    def __init__(self):
        self.value = "file handler error"
    def __str__(self):
        return repr(self.value)
class RtreeReadError(FileHandlerError):
    def __init__(self):
        self.value = "Error reading tree on disc, invalid offset or invalid data on file"
class RtreeWriteError(FileHandlerError):
    def __init__(self):
        self.value = "writing error, can't get type, expecting MRtree."
class RtreeDeleteError(FileHandlerError):
    def __init__(self):
        self.value = "deleting error, can't get type, expecting EmptyNode or EmptyLeaf."


# FILE HANDLERS

class RtreeFileHandler(object):
    def __init__(self, loadDataFile, dataFile, d, M, initOffset = 0):
        self.dataFile     = "data/" + dataFile
        self.loadDataFile = "data/" + loadDataFile

        self.M = M   # Cantidad maxima de entradas
        self.m = M/2 # Cantidad minima de entradas
        self.d = d   # dimension

        floatSize   = struct.calcsize("f")
        intSize     = struct.calcsize("i")
        booleanSize = struct.calcsize("?")

        self.mbrFloats   = 2*d*M # cantidad de flotantes para representar los mbrs
        self.pointerInts = M     # cantidad de enteros como punteros

        self.idBytes     = booleanSize                  # bytes de un id booleano
        self.mbrBytes    = self.mbrFloats*floatSize     # bytes de los mbrs
        self.pBytes      = self.pointerInts*intSize     # bytes de los punteros
        self.nodeBytes   = self.idBytes + self.mbrBytes + self.pBytes # tamaño total del nodo en bytes

        # En disco, el nodo se guarda de la siguiente manera:
        # ID MBR MBR MBR PUNTERO PUNTERO PUNTERO

        self.nodeId = True
        self.leafId = False

        self.elems  = []              # offsets de elementos en el arbol
        self.availableOffsets = []    # offsets disponibles para recupar
        self.lastOffset = initOffset  # ultimo offset del archivo donde es posible escribir mas nodos, o desde donde se comienza a leer

        # Creating Rtree file
        f = io.open(self.dataFile,'w+b')
        f.write("")
        f.close()

    def __str__(self):
        return "[RtreeFileHandler]{M:" + str(self.M) + ", m:" + str(self.m) + ", Id Bytes: " + str(self.idBytes) + ", Mbr Bytes :" + str(self.mbrBytes) + ", Pointer Bytes :" + str(self.pBytes) + "}"

    def write(self, buf, offset, dataFile = None):
        if dataFile == None:
            f = io.open(self.dataFile,  'r+b')
        else:
            f = io.open(dataFile,  'w+b')
        f.seek(offset)
        f.write(buf)

        if dataFile == None:
            if not offset in self.elems:
                self.elems = self.elems + [offset]
        f.close()

    def read(self, bytes, offset, dataFile = None):
        if dataFile == None:
            f = io.open(self.dataFile,  'r+b')
        else:
            f = io.open(dataFile,  'r+b')
        f.seek(offset)
        data = f.read(bytes)
        f.close()
        return data

    def getLastOffset(self):
        f = io.open(self.dataFile,'w+b')
        f.seek(-1)

    def deleteTree(self, data):
        pass

    # Guarda un arbol en disco
    def saveTree(self, tree):
        if tree.offset < 0 or  len(self.availableOffsets) == 0:
            # se trata de un arbol nuevo, o un arbol antiguo con algun error, por ende, se debe guardar al final del archivo
            tree.offset = self.lastOffset
            self.lastOffset = self.lastOffset + self.nodeBytes
        else:
            # se trata de un arbol que ya esta en disco, por ende, se guarda en una posicion disponible
            tree.offset = self.availableOffsets[0]
            self.availableOffsets = self.availableOffsets[1:]

        self.writeTree(tree)

    def writeTree(self, tree):
        t = type(tree)
        if t == MNode or t == MLeaf:
            mbrs     = tree.dumpMbrs()
            pointers = tree.dumpPointers()
            if t == MNode:
                idVal = self.nodeId
            else:
                idVal = self.leafId

            buf = struct.pack('1b', idVal) + struct.pack('%sf' % self.mbrFloats, *mbrs) + struct.pack('%si' % self.pointerInts,  *pointers)
            self.write(buf, tree.offset)
        else:
            raise RtreeWriteError()

    def isNode(self,offset):
        if offset < 0:
            return False
        elif type(self.readTree(offset)) == MNode:
            return True
        else:
            return False

    def readTree(self, offset):
        try:
            buf = self.read(self.nodeBytes, offset)

            bufId       = buf[0:self.idBytes]
            bufMbrs     = buf[self.idBytes : self.mbrBytes+1]
            bufPointers = buf[self.mbrBytes+1 : ]

            check     = (struct.unpack('1b', bufId))[0]
            mbrs      = struct.unpack('%sf' % self.mbrFloats, bufMbrs)
            pointers  = struct.unpack('%si' % self.pointerInts, bufPointers)
        except:
            raise RtreeReadError()

        if check == self.nodeId:
            return MNode(M = self.M, d = self.d, offset = offset, mbrs = mbrs, pointers = pointers)
        elif check == self.leafId:
            return MLeaf(M = self.M, d = self.d, offset = offset, mbrs = mbrs, pointers = pointers)

    def genData(self,dataFile,d,n):
        randVectors = [random.random() for _ in range(n)]
        buf         = struct.pack('1i',d) + struct.pack('1i',n) + struct.pack('%sd' % len(randVectors), *randVectors)
        self.write( buf, 0, dataFile)

    def getVectors(self):
        intSize    = struct.calcsize("i")
        doubleSize = struct.calcsize("d")
        offset     = 0

        d       = (struct.unpack('1i', self.read(bytes = intSize, offset = offset, dataFile = self.loadDataFile)))[0]
        offset  = offset + intSize

        size    = (struct.unpack('1i', self.read(bytes = intSize, offset = offset, dataFile = self.loadDataFile)))[0]
        offset  = offset + intSize

        vectorsBytes = size*doubleSize
        return struct.unpack('%sd' % size, self.read(bytes = vectorsBytes, offset = offset, dataFile = self.loadDataFile))

def ioTest():
    n = 10
    floatlist = [random.random() for _ in range(n)]
    buf = struct.pack('%sd' % n,  *floatlist)

    f = io.open('data/test.bin',  'wb')
    f.write(buf)

    f = io.open('data/test.bin',  'rb')
    buf = f.read(struct.calcsize("d")*n)
    floatlist2 = struct.unpack('%sd' % n,  buf)

    print(floatlist)
    print(floatlist2)
    print(floatlist[0] == floatlist2[0])

def nfhDataReadTest():
    d = 2
    blockBytes = 4096

    # nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
    #                         dataFile        = "rtree" + str(d) + "D.bin",
    #                         d = d,
    #                         blockBytes = blockBytes)
    # Generating data file
    # for j in range(1,21):
    #     nfh.genData("data" + str(j) + "D.bin", j, 100000)

    # for j in range(1,21):
        # dVectors = nfh.getVectors("data" + str(j) + "D.bin")
        # if j < 10:
            # space = "  "
        # else:
            # space = " "
        # print(str(j) + "D:" + space + str(dVectors))

def rtreeFileHandlerTest():
    d = 2
    M = 50

    nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
                            dataFile        = "TestRtree" + str(d) + "D.bin",
                            d = d,
                            M = 50)
    print(nfh)

    # Node write/read testing
    offset = 0
    mbrs = [0.5,0.6,0.1,0.15]*2
    pointers = [_ for _ in range(len(mbrs)/2/d)]

    # writing
    dataNode = MNode(M = nfh.M, d = nfh.d, offset = offset, mbrs = mbrs, pointers = pointers)
    # print(str(dataNode))
    nfh.writeTree(dataNode)

    # reading
    returnNode = nfh.readTree(offset)

    # comparing results
    print(str(dataNode))
    print(str(returnNode))

    # Leaf write/read testing
    offset = nfh.lastOffset

    # writing
    dataLeaf = MLeaf(M = nfh.M, d = d, offset = offset, mbrs = mbrs, pointers = pointers)
    nfh.writeTree(dataLeaf)

    # reading
    returnLeaf = nfh.readTree(offset)

    # comparing results
    print(str(dataLeaf))
    print(str(returnLeaf))

    # Testing polymorphic writing
    nfh.writeTree(dataLeaf)
    returnLeaf = nfh.readTree(offset)
    print(str(returnLeaf))

    nfh.saveTree(dataLeaf)
    returnLeaf = nfh.readTree(nfh.lastOffset - nfh.nodeBytes)
    nfh.saveTree(dataNode)
    returnNode = nfh.readTree(nfh.lastOffset - nfh.nodeBytes)

    print(str(returnLeaf))
    print(str(returnNode))

    print(nfh.elems)

if __name__=="__main__":
    ioTest()
    rtreeFileHandlerTest()