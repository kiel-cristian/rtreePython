# encoding: utf-8
import random
from Mbr import *


class PartitionError(Exception):
  def __init__(self, value="partition error"):
    self.value = value
  def __str__(self):
    return repr(self.value)

class PartitionAlgorithm():
  
  # Realiza la partición efectivamente
  # Retorna una lista con [[a,b],[a,b]] donde a es el mbr resultante y b es la lista de los indices que la componen
  def partition(self, mbrParent, mbrList):
    seedsIndex = self.selectSeeds(mbrParent, mbrList)
    restMbr = mList[:]
    restMbr.remove(mbrList[seedsIndex[0]])
    restMbr.remove(mbrList[seedsIndex[1]])
    seeds = [None, None]
    seeds[0] = mbrList[seedsIndex[0]]
    seeds[1] = mbrList[seedsIndex[1]]
    return self.partitionFromSeeds(seeds, restMbr)
    
  def selectSeeds(self, mbrParent, mbrList):
    pass
  
  def partitionFromSeeds(self, seeds, restMbr):
    pass

class LinealPartition(PartitionAlgorithm):
  def selectSeeds(self, mbrParent, mbrList):
    candidates = []
    candidatesIndex = []
    candidatesLen = 0
    # Obtenemos candidatos para semillas con los que estan en los bordes del mbr padre
    for i in range(0, len(mbrList)):
      mbr = mbrList[i]
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

  def partitionFromSeeds(self, seeds, restMbr):
    random.shuffle(restMbr)
    partitions = [[None, seeds[0]], [None, seeds[1]]]
    for mbr in restMbr:
      mbrExpanded1 = seeds[0].returnExpandedMBR(mbr)
      mbrExpanded2 = seeds[1].returnExpandedMBR(mbr)
      crec1 = mbrExpanded1.getArea() - seeds[0].getArea()
      crec2 = mbrExpanded2.getArea() - seeds[1].getArea()
      if crec1 < crec2:
        seeds[0] = mbrExpanded1
        partitions[0][0] = mbrExpanded1
        partitions[0] = partitions[0] + [mbr]
      else:
        seeds[1] = mbrExpanded2
        partitions[1][0] = mbrExpanded2
        partitions[1] = partitions[1] + [mbr]
    return partitions

class CuadraticPartition(PartitionAlgorithm):
  def selectSeeds(self, mbrParent, mbrList):
    length = len(mbrList)
    seedsIndex = [None , None]
    actualDeadSpace = 0;
    maxDeadSpace = 0
    # Calculamos el máximo espacio muerto
    for i in range(0, length):
      for j in range(i + 1, length):
        actualDeadSpace = mbrList[i].deadSpace(mbrList[j])
        if actualDeadSpace > maxDeadSpace:
            maxDeadSpace = actualDeadSpace
            seedsIndex = [i, j]
    return seedsIndex

  def partitionFromSeeds(self, seeds, restMbr):
    partitions = [[None, seeds[0]], [None, seeds[1]]]
    for mbr in restMbr:
      mbrExpanded1 = seeds[0].returnExpandedMBR(mbr)
      mbrExpanded2 = seeds[1].returnExpandedMBR(mbr)
      crec1 = mbrExpanded1.getArea() - (seeds[0].getArea() + mbr.getArea())
      crec2 = mbrExpanded2.getArea() - (seeds[1].getArea() + mbr.getArea())
      if crec1 < crec2:
        seeds[0] = mbrExpanded1
        partitions[0][0] = mbrExpanded1
        partitions[0] = partitions[0] + [mbr]
      else:
        seeds[1] = mbrExpanded2
        partitions[1][0] = mbrExpanded2
        partitions[1] = partitions[1] + [mbr]
    return partitions
  
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
  partitions = partition.partitionFromSeeds(seeds, restMbr)
  print([str(_) for _ in partitions[0]])
  print([str(_) for _ in partitions[1]])
  
if __name__ == "__main__":
  parent = Mbr(2)
  parent.setPoint([0, 1])
  mList = [Mbr(2).setPoint([0, 0.6]), Mbr(2).setPoint([0.5, 0.6]), Mbr(2).setPoint([0.5, 1]), Mbr(2).setPoint([0.5, 0.3]), Mbr(2).setPoint([1, 0.6]), Mbr(2).setPoint([0.7, 0])]
  print([str(_) for _ in mList])
  parent.setRange([0, 1, 0, 1])
  print("Linear")
  testPartition(LinealPartition(), parent, mList)
  print([ str(_) for e in LinealPartition().partition(parent, mList) for _ in e])
  print("Cuadratico")
  testPartition(CuadraticPartition(), parent, mList)
  print([ str(_) for e in CuadraticPartition().partition(parent, mList) for _ in e])
