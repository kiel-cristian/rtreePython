# encoding: utf-8
from Mbr import *
from MbrPointer import *
from SortingManager import *

class PartitionError(Exception):
  def __init__(self, value="partition error"):
    self.value = value
  def __str__(self):
    return repr(self.value)

class PartitionAlgorithm():
  
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
    return self.partitionFromSeeds(seeds, restMbr, m)
    
  def selectSeeds(self, mbrParent, mbrPointerList):
    pass
  
  def partitionFromSeeds(self, seeds, restMbr, m):
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

    # Obtenemos candidatos para semillas con los que estan en los bordes del mbr padre
    for i in range(0, len(mbrPointerList)):
      mbr = mbrPointerList[i]
      for d in range(mbrParent.d):
        if mbr.getMin(d) == mbrParent.getMin(d) or mbr.getMax(d) == mbrParent.getMax(d):
          candidates = candidates + [mbr]
          candidatesIndex = candidatesIndex + [i]
          candidatesLen = candidatesLen + 1

    if candidatesLen == 2:
      return [candidates, []] 
    if candidatesLen < 2:
      raise PartitionError("Se detectaron menos de 2 candidatos para particionar")

    seedsIndex = [None , None]
    actDist = 0;
    maxDistance = 0
    # Calculamos la máxima distancia entre los candidatos
    for i in range(0, candidatesLen):
      for j in range(i + 1, candidatesLen):
        actDist = candidates[i].distanceTo(candidates[j])
        if actDist > maxDistance:
            maxDistance = actDist
            seedsIndex = [candidatesIndex[i], candidatesIndex[j]]
    return seedsIndex

  def partitionFromSeeds(self, seeds, restMbr, m):
    # m : minimo de nodos en cada particion
    random.shuffle(restMbr)

    self.partitions = [[None, seeds[0]], [None, seeds[1]]]
    self.seeds = seeds
    self.pElems = [1,1]

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
    seedsIndex = [None , None]
    actualDeadSpace = 0;
    maxDeadSpace = 0
    # Calculamos el máximo espacio muerto
    for i in range(0, length):
      for j in range(i + 1, length):
        actualDeadSpace = mbrPointerList[i].deadSpace(mbrPointerList[j])
        if actualDeadSpace > maxDeadSpace:
            maxDeadSpace = actualDeadSpace
            seedsIndex = [i, j]
    return seedsIndex

  def partitionFromSeeds(self, seeds, restMbr, m):
    self.partitions = [[None, seeds[0]], [None, seeds[1]]]
    self.seeds = seeds
    self.pElems = [1,1]

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
  def mbrCompare(self, d):
    def compare(first, second):
        firstDMin  = first.getMbr().getMin(d)
        secondDMin = second.getMbr().getMin(d)
        c = 0
        if  firstDMin < secondDMin:
          c = -1
        elif firstDMin > secondDMin:
          c = 1
        return c
    return compare

  def partition(self, mbrParent, mbrPointerList, m):
    dimensionSortedList = []
    minCost = len(mbrPointerList)**2 + 1 # cota superior cuadratica
    sorter = SortingManager()

    for d in range(mbrParent.d):
      dimensionSortedList = dimensionSortedList + [sorter.mergesort(self.mbrCompare(d), mbrPointerList)]
      if sorter.cost < minCost:
        minCost = d

    sortedList = dimensionSortedList[minCost]
    firstPartition  = sortedList[0:m]
    secondPartition = sortedList[m:]

    mbrs = [firstPartition[0].getMbr(), secondPartition[0].getMbr()]
    for m in firstPartition[1:]:
      mbrs[0].expand(m.getMbr())

    for m in secondPartition[1:]:
      mbrs[1].expand(m.getMbr())

    return [[mbrs[0]] + firstPartition, [mbrs[1]] + secondPartition]

  def partitionFromSeeds(self, seeds, restMbr, m):
    self.partitions = [[None, seeds[0]], [None, seeds[1]]]
    self.seeds = seeds

    i = 1
    for m in restMbr:
      if i < m:
        self.addToFirstPartition(m)
      else:
        self.addToSecondPartition(m)
      i = i + 1

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
  partitions = partition.partitionFromSeeds(seeds, restMbr, 2)
  print("Partitions:")
  print([str(_) for _ in partitions[0]])
  print([str(_) for _ in partitions[1]])

def newMbrPointer(point):
  return MbrPointer(Mbr(2).setPoint(point), 0)
  
if __name__ == "__main__":
  parent = Mbr(2)
  parent.setPoint([0, 1])
  mList = [newMbrPointer([0, 0.6]), newMbrPointer([0.5, 0.6]), newMbrPointer([0.5, 1]), newMbrPointer([0.5, 0.3]), newMbrPointer([1, 0.6]), newMbrPointer([0.7, 0])]
  print([str(_) for _ in mList])
  parent.setRange([0, 1, 0, 1])

  print("Linear")
  testPartition(LinealPartition(), parent, mList)
  print([ str(_) for e in LinealPartition().partition(parent, mList, 2) for _ in e])

  print("Cuadratico")
  testPartition(CuadraticPartition(), parent, mList)
  print([ str(_) for e in CuadraticPartition().partition(parent, mList, 2) for _ in e])

  print("Sweep")
  print([ str(_) for e in SweepPartition().partition(parent, mList, 2) for _ in e])