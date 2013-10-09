import io
import sys
from MRtree import *
import random
import struct

# ERRORS
class FileHandlerError(Exception):
    def __init__(self):
        self.value = "file handler error"
    def __str__(self):
        return repr(self.value)

class RtreeReadError(FileHandlerError):
    pass
class RtreeNodeReadError(FileHandlerError):
    pass
class RtreeLeafReadError(FileHandlerError):
    pass
class RtreeWriteError(FileHandlerError):
    def __init__(self):
        self.value = "writing error, can't get type, expecting MRtree."
class RtreeDeleteError(FileHandlerError):
    def __init__(self):
        self.value = "deleting error, can't get type, expecting EmptyNode or EmptyLeaf."


# FILE HANDLERS

class RtreeFileHandler(object):
    def __init__(self, loadDataFile, dataFile, d, M):

        self.dataFile = dataFile
        self.loadDataFile = loadDataFile

        self.M = M   # Cantidad maxima de entradas
        self.m = M/2 # Cantidad minima de entradas
        self.d = d   # dimension

        floatSize   = struct.calcsize("f")
        intSize     = struct.calcsize("i")
        booleanSize = struct.calcsize("?")

        # bytes de un boolean
        idBytes     = booleanSize
        # bytes de un mbr
        mbrBytes    = 2*d*floatSize
        # bytes de todas las tuplas (mbr, puntero)
        tuplesBytes = M*(1 + mbrBytes + struct.calcsize("i"))

        self.tuplesBytes = tuplesBytes
        self.idBytes     = idBytes
        self.mbrBytes    = mbrBytes
        self.nodeBytes   = tuplesBytes + idBytes

        self.nodeId = True
        self.leafId = False

        self.elems  = []
        self.availableOffsets = []
        self.lastOffset = 0

        # Creating Rtree file
        f = io.open(self.dataFile,'w+b')
        f.write("")
        f.close()

    def printInfo(self):
        print "M:" + str(self.M)
        print "m:" + str(self.m)
        print "Id Bytes: " + str(self.idBytes)
        print "Tuples Bytes :" + str(self.tuplesBytes)

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

    def deleteTree(self, data):
        if type(data) == EmptyNode:
            self.writeNode(data)
            self.availableOffsets = self.availableOffsets + data.offset
        elif type(data) == EmptyLeaf:
            self.writeLeaf(data)
            self.availableOffsets = self.availableOffsets + data.offset
        else:
            raise RtreeDeleteError()

    def addTree(self,data):
        if len(self.availableOffsets) > 0:
            data.offset = self.availableOffsets[0]
            self.availableOffsets = self.availableOffsets[1:]
        else:
            data.offset = self.lastOffset
        self.writeTree(data)
        self.lastOffset = self.lastOffset + self.nodeBytes

    def writeTree(self, data):
        t = type(data)
        if t == MNode:
            self.writeNode(data)
        elif t == MLeaf:
            self.writeLeaf(data)
        else:
            raise RtreeWriteError()

    def writeNode(self, dataNode):
        mbrs     = dataNode.dumpMbrs()
        pointers = dataNode.dumpPointers()
        idVal    = self.nodeId


        print mbrs
        print len(mbrs)
        print pointers
        print len(pointers)
        print idVal

        print struct.pack('%sd' % (self.M + 1)*self.d*2, *mbrs) 

        buf = struct.pack('1b', idVal) + struct.pack('%sd' % (self.M + 1)*self.d*2, *mbrs) + struct.pack('%si' % self.M,  *pointers)
        self.write(buf, dataNode.offset)

    def writeLeaf(self, dataLeaf):
        mbrs     = dataLeaf.dumpMbrs()
        pointers = dataLeaf.dumpPointers()
        idVal    = self.leafId

        buf = struct.pack('1b', idVal) + struct.pack('%sd' % (self.M + 1)*self.d*2, *mbrs) + struct.pack('%si' % self.M,  *pointers)
        self.write(buf, dataLeaf.offset)

    def isNode(self,offset):
        if offset < 0:
            return False
        elif type(self.readTree(offset)) == MNode:
            return True
        else:
            return False

    def readTree(self, offset):
        buf = self.read(self.nodeBytes, offset)
        bufId = buf[0:self.idBytes]
        check = (struct.unpack('1b', bufId))[0]

        if check == self.nodeId:
            return self.readNode(offset, buf)
        elif check == self.leafId:
            return self.readLeaf(offset, buf)
        else:
            raise RtreeReadError()

    def readNode(self, offset, buf):
        try:
            buf1 = buf[self.idBytes : self.mbrBytes + self.tuplesBytes+1]
            buf2 = buf[self.mbrBytes + self.tuplesBytes + 1 : self.nodeBytes]

            mbrs      = struct.unpack('%sd' % (self.M + 1)*self.d*2,  buf1)
            pointers  = struct.unpack('%si' % self.M,  buf2)

            return MNode(maxE = self.p, d = self.d, offset = offset, mbrs = mbr, pointers = pointers)
        except:
            raise RtreeNodeReadError()

    def readLeaf(self, offset, buf):
        try:
            buf1 = buf[self.idBytes : self.mbrBytes + self.tuplesBytes+1]
            buf2 = buf[self.mbrBytes + self.tuplesBytes + 1 : self.nodeBytes]

            mbrs      = struct.unpack('%sd' % (self.M + 1)*self.d*2,  buf1)
            pointers  = struct.unpack('%si' % self.M,  buf2)
            return MLeaf(maxE = self.v, d = self.d, offset = offset, mbrs = mbr, pointers = vectors)
        except:
            raise RtreeLeafReadError()

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

    print floatlist
    print floatlist2
    print floatlist[0] == floatlist2[0]

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
        # print str(j) + "D:" + space + str(dVectors)

def rtreeFileHandlerTest():
    d = 2
    M = 50

    nfh = RtreeFileHandler( loadDataFile    = "data" + str(d) + "D.bin",
                            dataFile        = "rtree" + str(d) + "D.bin",
                            d = d,
                            M = 50)
    nfh.printInfo()

    # Node write/read testing
    offset = 0
    mbrs = [0.5,0.6,0.1,0.15]*2
    pointers = [_ for _ in range(1)]

    # writing
    dataNode = MNode(M = nfh.M, d = nfh.d, offset = offset, mbrs = mbrs, pointers = pointers)
    # dataNode.printRtree()
    nfh.writeNode(dataNode)

    # reading
    returnNode = nfh.readTree(offset)

    # comparing results
    dataNode.printRtree()
    returnNode.printRtree()

    # Leaf write/read testing
    offset = nfh.lastOffset

    # writing
    dataLeaf = MLeaf(M = nfh.v, d = d, offset = offset, mbrs = mbrs, pointers = pointers)
    nfh.writeLeaf(dataLeaf)

    # reading
    returnLeaf = nfh.readTree(offset)

    # comparing results
    dataLeaf.printRtree()
    returnLeaf.printRtree()

    # Testing polymorphic writing
    nfh.writeTree(dataLeaf)
    returnLeaf = nfh.readTree(offset)
    returnLeaf.printRtree()

    nfh.addTree(dataLeaf)
    returnLeaf = nfh.readTree(nfh.lastOffset - nfh.nodeBytes)
    nfh.addTree(dataNode)
    returnNode = nfh.readTree(nfh.lastOffset - nfh.nodeBytes)

    returnLeaf.printRtree()
    returnNode.printRtree()

    print nfh.elems

if __name__=="__main__":
    ioTest()
    rtreeFileHandlerTest()