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
    def __init__(self, dataFile, d, blockBytes, nodeBytes, leafBytes, idBytes, rBytes,  pBytes, vBytes):
        self.dataFile = dataFile                          # Data file where Rtree is stored
        self.bBytes = blockBytes                          # disk block bytes
        self.nBytes = nodeBytes                           # node bytes
        self.lBytes = leafBytes                           # leaf bytes
        self.idBytes = idBytes                            # identifier bytes
        self.rBytes = rBytes                              # number of node mbr bytes
        self.pBytes = pBytes                              # number of node pointers bytes
        self.vBytes = vBytes                              # numer of vector bytes of a leaf
        self.d = d                                          # Dimension

        intSize   = struct.calcsize("i")
        floatSize = struct.calcsize("d")
        boolSize  = struct.calcsize("?")

        self.r = int(rBytes/floatSize)
        self.p = int(pBytes/intSize)
        self.v = int(vBytes/floatSize)
        self.nodeId = True
        self.leafId = False

        self.elems = []
        self.availableOffsets = []
        self.lastOffset = 0

        # Creating Rtree file
        f = io.open(self.dataFile,'w+b')
        f.write("")
        f.close()

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
        self.lastOffset = self.lastOffset + self.bBytes

    def writeTree(self, data):
        t = type(data)
        if t == MNode or t == EmptyNode:
            self.writeNode(data)
        elif t == MLeaf or t == EmptyLeaf:
            self.writeLeaf(data)
        else:
            raise RtreeWriteError()

    def writeNode(self, dataNode):
        ranges   = dataNode.mbr
        pointers = dataNode.pointers
        idVal   = self.nodeId

        buf = struct.pack('1b', idVal) + struct.pack('%sd' % self.r,  *ranges) + struct.pack('%si' % self.p,  *pointers)
        self.write(buf, dataNode.offset)

    def writeLeaf(self, dataLeaf):
        vectors = dataLeaf.vectors
        idVal = self.leafId

        buf = struct.pack('1b', idVal) + struct.pack('%sd' % self.v,  *vectors)
        self.write(buf, dataLeaf.offset)

    def isNode(self,offset):
        if offset < 0:
            return False
        elif type(self.readTree(offset)) == MNode:
            return True
        else:
            return False

    def readTree(self, offset):
        buf = self.read(self.bBytes, offset)
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
            buf1 = buf[self.idBytes:self.rBytes+1]
            buf2 = buf[self.rBytes+1:self.nBytes]

            mbr      = struct.unpack('%sd' % self.r,  buf1)
            pointers = struct.unpack('%si' % self.p,  buf2)
            return MNode(maxE = self.p, d = self.d, offset = offset, mbr = mbr, pointers = pointers)
        except:
            raise RtreeNodeReadError()

    def readLeaf(self, offset, buf):
        try:
            adjBuf = buf[0:self.lBytes]
            bufLeaf = adjBuf[self.idBytes:self.lBytes]

            vectors = struct.unpack('%sd' % self.v,  bufLeaf)
            return MLeaf(maxE = self.v, d = self.d, offset = offset, vectors = vectors)
        except:
            raise RtreeLeafReadError()

    def genData(self,dataFile,d,n):
        randVectors = [random.random() for _ in range(n)]
        buff         = struct.pack('1i',d) + struct.pack('1i',n) + struct.pack('%sd' % len(randVectors), *randVectors)
        self.write( buff, 0, dataFile)

    def getVectors(self, vectorsFile):
        intSize    = struct.calcsize("i")
        doubleSize = struct.calcsize("d")
        offset      = 0

        d       = (struct.unpack('1i', self.read(bytes = intSize, offset = offset, dataFile = vectorsFile)))[0]
        offset  = offset + intSize

        size    = (struct.unpack('1i', self.read(bytes = intSize, offset = offset, dataFile = vectorsFile)))[0]
        offset  = offset + intSize

        vectorsBytes = size*doubleSize
        return struct.unpack('%sd' % size, self.read(bytes = vectorsBytes, offset = offset, dataFile = vectorsFile))

def ioTest():
    n = 10
    floatlist = [random.random() for _ in range(n)]
    buf = struct.pack('%sd' % n,  *floatlist)

    f = io.open('test.bin',  'wb')
    f.write(buf)

    f = io.open('test.bin',  'rb')
    buf = f.read(struct.calcsize("d")*n)
    floatlist2 = struct.unpack('%sd' % n,  buf)

    print floatlist
    print floatlist2
    print floatlist[0] == floatlist2[0]

def rtreeFileHandlerTest():
    d           = 2
    bBytes     = 4096
    idBytes    = struct.calcsize("?")
    rBytes     = 2*d*struct.calcsize("d")
    pBytes     = bBytes - idBytes - rBytes
    vBytes     = bBytes - idBytes

    print "Id Bytes: " + str(idBytes)
    print "Pointers Bytes: " + str(pBytes)
    print "Region Bytes: " + str(rBytes)
    print "Vectors Bytes: " + str(vBytes)

    # adjustment
    pBytes = pBytes - pBytes % struct.calcsize("i")
    vBytes = vBytes - vBytes % struct.calcsize("d")

    print "Adj Pointers Bytes: " + str(pBytes)
    print "Adj Vectors Bytes: " + str(vBytes)

    nBytes = rBytes + pBytes + idBytes
    lBytes = idBytes + vBytes

    print "Node Bytes:" + str(nBytes)
    print "Leaf Bytes:" + str(lBytes)

    nfh = RtreeFileHandler( dataFile = "rtree" + str(d) + "D.bin",
                            d = d,
                            blockBytes = bBytes,
                            nodeBytes = nBytes,
                            leafBytes = lBytes,
                            idBytes = idBytes,
                            rBytes = rBytes,
                            pBytes = pBytes,
                            vBytes = vBytes)

    # Node write/read testing
    offset = 0
    mbr = [0.5,0.6,0.1,0.15]
    pointers = [nBytes+1, nBytes*2 + 1]

    # writing
    dataNode = MNode(maxE = nfh.p, d = d, offset = offset, mbr = mbr, pointers = pointers)
    dataNode.set(mbr, pointers)
    nfh.writeNode(dataNode)

    # reading
    returnNode = nfh.readTree(offset)

    # comparing results
    dataNode.printRtree()
    returnNode.printRtree()

    # Leaf write/read testing
    offset = nfh.lastOffset
    vectors = [0.23,0.45,0.56,-0.1]

    # writing
    dataLeaf = MLeaf(maxE = nfh.v, d = d, offset = offset, vectors = vectors)
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
    returnLeaf = nfh.readTree(nfh.lastOffset - bBytes)
    nfh.addTree(dataNode)
    returnNode = nfh.readTree(nfh.lastOffset - bBytes)

    returnLeaf.printRtree()
    returnNode.printRtree()

    print nfh.elems

    # Generating data file
    # for j in range(1,21):
    #     nfh.genData("data" + str(j) + "D.bin", j, 100000)

    for j in range(1,21):
        dVectors = nfh.getVectors("data" + str(j) + "D.bin")
        if j < 10:
            space = "  "
        else:
            space = " "
        # print str(j) + "D:" + space + str(dVectors)

if __name__=="__main__":
    ioTest()
    rtreeFileHandlerTest()