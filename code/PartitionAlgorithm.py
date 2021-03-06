# encoding: utf-8
from Mbr import *
from MbrPointer import *
from SortingManager import *

class PartitionError(Exception):
    def __init__(self, value="partition error"):
        super(PartitionError, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)

class PartitionAlgorithm(object):
    def __init__(self):
        self.partitions = []
        self.seeds      = []
        self.pElems     = 0

    # Realiza la partición efectivamente
    # Retorna una lista con [[a,b],[a,b]] donde a es el mbr resultante y b es la lista de los indices que la componen
    def partition(self, mbrParent, mbrPointerList, m):
        seedsIndex = self.selectSeeds(mbrParent, mbrPointerList)
        restMbr = mbrPointerList[:]
        restMbr.remove(mbrPointerList[seedsIndex[0]])
        restMbr.remove(mbrPointerList[seedsIndex[1]])
        seeds = [None, None]
        seeds[0] = mbrPointerList[seedsIndex[0]]
        seeds[1] = mbrPointerList[seedsIndex[1]]

        self.partitions = [[seeds[0].getMbr(), seeds[0]], [seeds[1].getMbr(), seeds[1]]]
        self.seeds = seeds
        self.pElems = [1,1]

        return self.partitionFromSeeds(restMbr, m)

    def selectSeeds(self, mbrParent, mbrPointerList):
        pass

    def partitionFromSeeds(self, restMbr, m):
        pass

    def addToPartition(self, mbr, i):
        mbrExpanded = self.getPartitionExpand(i, mbr)
        self.seeds[i] = mbrExpanded
        self.partitions[i][0] = mbrExpanded
        self.partitions[i] = self.partitions[i] + [mbr]
        self.pElems[i] = self.pElems[i] + 1

    def addToFirstPartition(self, mbr):
        self.addToPartition(mbr, 0)

    def addToSecondPartition(self, mbr):
        self.addToPartition(mbr, 1)

    def getPartitionExpand(self,i, mbr):
        return self.seeds[i].returnExpandedMBR(mbr)

    def getFirstPartitionExpand(self, mbr):
        return self.getPartitionExpand(0, mbr)

    def getSecondPartitionExpand(self, mbr):
        return self.getPartitionExpand(1, mbr)

    def getSeedIncrement(self, i, mbr):
        return mbr.getArea() - self.seeds[i].getArea()

    def getFirstSeedIncrement(self, mbr):
        return self.getSeedIncrement(0, mbr)

    def getSecondSeedIncrement(self, mbr):
        return self.getSeedIncrement(1, mbr)

    def getDeadSpaceIncrement(self, expanded, i, mbr):
        return expanded.getArea() - self.seeds[i].getArea() - mbr.getArea()

    def getFirstDeadSpaceIncrement(self, expanded, mbr):
        return self.getDeadSpaceIncrement(expanded, 0, mbr)

    def getSecondDeadSpaceIncrement(self, expanded, mbr):
        return self.getDeadSpaceIncrement(expanded, 1, mbr)

    def firstPElems(self):
        return self.pElems[0]

    def secondPElems(self):
        return self.pElems[1]

class LinealPartition(PartitionAlgorithm):
    def selectSeeds(self, mbrParent, mbrPointerList):
        candidates = []
        candidatesIndex = []
        candidatesLen = 0
        length = len(mbrPointerList)

        # Obtenemos candidatos para semillas con los que estan en los bordes del mbr padre
        for i in range(length):
            mbr = mbrPointerList[i]
            for d in range(mbrParent.d):
                if mbr.getMin(d) == mbrParent.getMin(d) or mbr.getMax(d) == mbrParent.getMax(d):
                    candidates = candidates + [mbr]
                    candidatesIndex = candidatesIndex + [i]
                    candidatesLen = candidatesLen + 1
                    break

        if candidatesLen == 2:
            return candidatesIndex

        if candidatesLen < 2: # 1 mbr abarca toda el area!
            candidates = mbrPointerList[:]
            candidatesLen = length
            candidatesIndex = [i for i in range(length)]

        seedsIndex = [0 , 1]
        actDist = 0;
        maxDistance = 0
        # Calculamos la máxima distancia entre los candidatos
        for i in range(candidatesLen):
            for j in range(i + 1, candidatesLen):
                actDist = candidates[i].distanceTo(candidates[j])
                if actDist > maxDistance:
                        maxDistance = actDist
                        seedsIndex = [candidatesIndex[i], candidatesIndex[j]]
        return seedsIndex

    def partitionFromSeeds(self, restMbr, m):
        # m : minimo de nodos en cada particion
        random.shuffle(restMbr)
        for mbr in restMbr:
            if self.secondPElems() == m:
                self.addToFirstPartition(mbr)
            elif self.firstPElems() == m:
                self.addToSecondPartition(mbr)
            else:
                mbrExpanded1 = self.getFirstPartitionExpand(mbr)
                mbrExpanded2 = self.getSecondPartitionExpand(mbr)
                crec1 = self.getFirstSeedIncrement(mbrExpanded1)
                crec2 = self.getSecondSeedIncrement(mbrExpanded2)

                if crec1 < crec2:
                    self.addToFirstPartition(mbr)
                else:
                    self.addToSecondPartition(mbr)
        return self.partitions

class CuadraticPartition(PartitionAlgorithm):
    def selectSeeds(self, mbrParent, mbrPointerList):
        length = len(mbrPointerList)
        seedsIndex = [0, 1]
        actualDeadSpace = 0
        maxDeadSpace = 0
        # Calculamos el máximo espacio muerto
        for i in range(length):
            for j in range(i + 1, length):
                actualDeadSpace = mbrPointerList[i].deadSpace(mbrPointerList[j])
                if actualDeadSpace > maxDeadSpace:
                        maxDeadSpace = actualDeadSpace
                        seedsIndex = [i, j]
        return seedsIndex

    def partitionFromSeeds(self, restMbr, m):
        for mbr in restMbr:
            if self.secondPElems() == m:
                self.addToFirstPartition(mbr)
            elif self.firstPElems() == m:
                self.addToSecondPartition(mbr)
            else:
                mbrExpanded1 = self.getFirstPartitionExpand(mbr)
                mbrExpanded2 = self.getSecondPartitionExpand(mbr)
                crec1 = self.getFirstDeadSpaceIncrement(mbrExpanded1, mbr)
                crec2 = self.getSecondDeadSpaceIncrement(mbrExpanded2, mbr)
                if crec1 < crec2:
                    self.addToFirstPartition(mbr)
                else:
                    self.addToSecondPartition(mbr)
        return self.partitions

# Particion usada por el R+ tree
class SweepPartition(PartitionAlgorithm):
    def __init__(self):
        super(SweepPartition, self).__init__()
        self.sorter = SortingManager()
        self.cut = None
        self.dim = None
        self.recursiveSplits = None

    def mbrCompare(self, d):
        def compare(first, second):
            firstDMin    = first.getMbr().getMin(d)
            secondDMin = second.getMbr().getMin(d)
            c = 0
            if    firstDMin < secondDMin:
                c = -1
            elif firstDMin > secondDMin:
                c = 1
            return c
        return compare

    # La particion se basa en lo siguiente:
    # Determina un corte utilizando un orden parcial de los mbrs para determinada dimension d, donde el coste de ordenar la lista en base a dimension
    # es el menor coste. Luego, contruye dos particiones en base a este corte dimensional, si se trata de un nodo hoja, los elementos deben reinsertarse
    # en toda particion donde intersecten
    def partition(self, mbrParent, mbrPointerList, m, leafMode = False):
        dimensionSortedList = []
        minCostDim = len(mbrPointerList)**2 + 1 # cota superior cuadratica

        for d in range(mbrParent.d):
            dimensionSortedList = dimensionSortedList + [self.sorter.mergesort(self.mbrCompare(d), mbrPointerList)]
            if self.sorter.cost < minCostDim:
                minCostDim = d

        sortedList = dimensionSortedList[minCostDim]
        dimCut = (sortedList[m-1].getMin(minCostDim) + sortedList[m].getMin(minCostDim))/2 #corte dimensional
        seedMbrs = mbrParent.cutOnDimension(minCostDim, dimCut) # mbr de las dos nuevas particiones

        recursiveSplits = []
        firstPartition    = []
        secondPartition = []
        rs = 0

        if leafMode:
            fPLen = 0
            sPLen = 0

            for mb in sortedList:
                if seedMbrs[0].areIntersecting(mb):
                    firstPartition = firstPartition + [mb]
                    fPLen = fPLen + 1
                if seedMbrs[1].areIntersecting(mb):
                    secondPartition = secondPartition + [mb]
                    sPLen = sPLen + 1

            maxL = len(mbrPointerList)

            if fPLen == maxL or sPLen == maxL:
                raise PartitionError("Particion Sweep no separo de forma adecuada los elementos en las hojas")
            elif fPLen + sPLen < maxL:
                raise PartitionError("Particion perdio elementos")
        else:
            i = 0
            for mb in sortedList:
                # Si es que el corte atraviesa al mbr, es necesario subdividirlo recursivamente posteriormente
                if mb.getMin(minCostDim) >= dimCut and dimCut <= mb.getMax(minCostDim):
                    recursiveSplits = recursiveSplits + [mb]
                    rs = rs + 1
                elif mb.getMin(minCostDim) < dimCut and i < m:
                    firstPartition = firstPartition + [mb]
                    i = i +1
                else:
                    secondPartition = secondPartition + [mb]

        if rs > 0:
            self.cut = dimCut
            self.dim = minCostDim
            self.recursiveSplits = recursiveSplits
        else:
            self.cut = None
            self.dim = None
            self.recursiveSplits = []
        return [[seedMbrs[0]] + firstPartition, [seedMbrs[1]] + secondPartition]

    # Particiona una lista de mbrPointers segun un corte dimensional, y, almacena los nodos
    # que deben ser particionados de forma recursiva antes de insertarlos
    def partitionOnCut(self, mbrPointerList, cut, dim):
        firstPartition  = []
        secondPartition = []
        recursiveSplits = []
        rs = 0

        for mb in mbrPointerList:
            # Corte en nodo hijo
            if mb.getMin(dim)<= cut and cut <= mb.getMax(dim):
                recursiveSplits = recursiveSplits + [mb]
                rs = rs + 1
            elif mb.getMax(dim) <= cut:
                firstPartition = firstPartition + [mb]
            else:
                secondPartition = secondPartition + [mb]

        if rs > 0:
            self.cut = cut
            self.dim = dim
            self.recursiveSplits = recursiveSplits
        else:
            self.cut = None
            self.dim = None
            self.recursiveSplits = []
        return [firstPartition, secondPartition]

    def getCut(self):
        return self.cut
    def getDim(self):
        return self.dim
    def getRecursiveSplits(self):
        return self.recursiveSplits
    def needsToSplitChilds(self):
        return self.cut != None

def testPartition(partition, parent, mList):
    seedsIndex = partition.selectSeeds(parent, mList)
    print(seedsIndex)
    restMbr = mList[:]
    restMbr.remove(mList[seedsIndex[0]])
    restMbr.remove(mList[seedsIndex[1]])
    seeds = [None, None]
    seeds[0] = mList[seedsIndex[0]]
    seeds[1] = mList[seedsIndex[1]]
    print([str(_) for _ in seeds])
    print([str(_) for _ in restMbr])
    partition.partitions = [[seeds[0].getMbr(), seeds[0]], [seeds[1].getMbr(), seeds[1]]]
    partition.seeds = seeds
    partition.pElems = [1,1]
    partitions = partition.partitionFromSeeds(restMbr, 2)
    print("Partitions:")
    print([str(_) for _ in partitions[0]])
    print([str(_) for _ in partitions[1]])

# Nuevo MbrPointer con puntero fijo
def newMbrPointer(point):
    return MbrPointer(Mbr(2).setPoint(point), 0)

if __name__ == "__main__":
    parent = Mbr(2)
    parent.setPoint([0.0, 1.0])
    mList    = [newMbrPointer([0.0, 0.6]), newMbrPointer([0.5, 0.6]), newMbrPointer([0.5, 1.0]), newMbrPointer([0.5, 0.3]), newMbrPointer([1.0, 0.6]), newMbrPointer([0.7, 0.0])]
    print([str(_) for _ in mList])
    parent.setRange([0.0, 1.0, 0.0, 1.0])

    print("Linear")
    testPartition(LinealPartition(), parent, mList)
    print([ str(_) for e in LinealPartition().partition(parent, mList, 2) for _ in e])

    print("Cuadratico")
    testPartition(CuadraticPartition(), parent, mList)
    print([ str(_) for e in CuadraticPartition().partition(parent, mList, 2) for _ in e])

    print("Sweep")
    sp = SweepPartition()
    print([ str(_) for e in sp.partition(parent, mList, 2) for _ in e])
    print([ str(_) for _ in sp.partition(parent, mList, 2, True)[0]])
    print([ str(_) for _ in sp.partition(parent, mList, 2, True)[1]])
    print("By Cut")
    print("cut on 0.3")
    cuts = sp.partitionOnCut(mList, 0.3, 0)
    print([str(_) for _ in cuts[0]])
    print([str(_) for _ in cuts[1]])
    print("recursive splits")
    print([str(_) for _ in sp.getRecursiveSplits()])
    print("cut on 0.5")
    cuts = sp.partitionOnCut(mList, 0.5, 0)
    print([str(_) for _ in cuts[0]])
    print([str(_) for _ in cuts[1]])
    print("recursive splits")
    print([str(_) for _ in sp.getRecursiveSplits()])