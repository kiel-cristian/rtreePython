from Mbr import *

class PartitionError(Exception):
  def __init__(self, value = "partition error"):
    self.value = value
  def __str__(self):
    return repr(self.value)

class PartitionAlgorithm():
  def selectSeeds(self, mbrParent, mbrList):
    pass
  def doPartition(self, seed1, seed2, mbrList):
    pass

class LinealPartition(PartitionAlgorithm):
  def selectSeeds(self, mbrParent, mbrList):
    candidates    = []
    candidatesLen = 0

    for mbr in mbrList:
      for d in range(mbrParent.d):
        if mbr.dRanges[d][0] == mbrParent[d][0] or mbr.dRanges[d][1] == mbrParent[d][1]:
          candidates = candidates + mbr
          candidatesLen = candidates + 1

    if candidatesLen == 2:
      return candidates
    if candidatesLen < 2:
      raise PartitionError("Se detectaron menos de 2 candidatos para particionar")

    seed1 = candidates[0]
    seed2 = candidates[-1]

    maxDistance = seed1.distanceTo(seed2)

    i = 1
    j = candidatesLen - 1

    while i < j:
      

  def doPartition(self, seed1, seed2, mbrList):
    pass

class CuadraticPartition(PartitionAlgorithm):
  def selectSeeds(self, mbrParent, mbrList):
    pass
  def doPartition(self, seed1, seed2, mbrList):
    pass