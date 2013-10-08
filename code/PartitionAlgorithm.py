from Mbr import *

class PartitionError(Exception):
  def __init__(self, value="partition error"):
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
    mList = mbrList[:]
    candidates = []
    candidatesLen = 0

    for mbr in mList:
      for d in range(mbrParent.d):
        if mbr.getMin(d) == mbrParent.getMin(d) or mbr.getMax(d) == mbrParent.getMax(d):
          candidates = candidates + [mbr]
          candidatesLen = candidatesLen + 1

    if candidatesLen == 2:
      return [candidates, []] 
    if candidatesLen < 2:
      raise PartitionError("Se detectaron menos de 2 candidatos para particionar")

    seeds = [None , None]
    actDist = 0;
    maxDistance = 0
    # Calculamos la máxima distancia entre los candidatos
    for i in range(0, candidatesLen):
      for j in range(1, candidatesLen):
        actDist = candidates[i].distanceTo(candidates[j])
        if actDist > maxDistance:
            maxDistance = actDist
            seeds = [candidates[i], candidates[j]]
            
    mList.remove(seeds[0])
    mList.remove(seeds[1])
    return [seeds, mList]

  def doPartition(self, seed1, seed2, mbrList):
    pass

class CuadraticPartition(PartitionAlgorithm):
  def selectSeeds(self, mbrParent, mbrList):
    mList = mbrList[:]
    candidates = []
    candidatesLen = 0

    for mbr in mList:
      for d in range(mbrParent.d):
        if mbr.getMin(d) == mbrParent.getMin(d) or mbr.getMax(d) == mbrParent.getMax(d):
          candidates = candidates + [mbr]
          candidatesLen = candidatesLen + 1

    if candidatesLen == 2:
      return [candidates, []] 
    if candidatesLen < 2:
      raise PartitionError("Se detectaron menos de 2 candidatos para particionar")

    seeds = [None , None]
    actDist = 0;
    maxDistance = 0
    # Calculamos la máxima distancia entre los candidatos
    for i in range(0, candidatesLen):
      for j in range(1, candidatesLen):
        actDist = candidates[i].distanceTo(candidates[j])
        if actDist > maxDistance:
            maxDistance = actDist
            seeds = [candidates[i], candidates[j]]
            
    mList.remove(seeds[0])
    mList.remove(seeds[1])
    return [seeds, mList]

  def doPartition(self, seed1, seed2, mbrList):
    pass
  
if __name__ == "__main__":
  parent=Mbr(2)
  parent.setPoint([0,1])
  list=[Mbr(2).setPoint([0,0.6]),Mbr(2).setPoint([0.5,0.6]),Mbr(2).setPoint([0.5,1]),Mbr(2).setPoint([0.5,0.3]),Mbr(2).setPoint([1,0.6]),Mbr(2).setPoint([0.7,0])]
  parent.setRange([0,1,0,1])
  LinealPartition().selectSeeds(parent, list)