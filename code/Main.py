'''
Created on 09-10-2013

@author: Ian
'''
import io
import random
import struct
import Rtree
import Mbr


def generateObjects(name, numElems, dimension):
  f = io.open(name, 'wb')
  randElems = [random.random() for _ in range(numElems * dimension)]
  buf = struct.pack('1i', dimension) + struct.pack('1i', numElems) + struct.pack('%sd' % len(randElems), *randElems)
  f.write(buf)
  print("Done[" + str(numElems) + "," + str(dimension) + "]")
  
def generateData():
  num = 0;
  for d in range(1, 9):
    for n in range (1, 11):
      generateObjects("data" + str(num), n * (10 ** 5), 2 ** d)
      num = num + 1

if __name__ == '__main__':
    # generateData()
  f = open("Resultados.txt", 'w+')
  for d in range(1, 9):
    mTree = Rtree(2 ** d)
    for n in range (1, 11):
      f.write("d n meanPartitionsPerNode meanInsertTime meanTotalNodes meanInternalNodes\n")
      # Construyo el RTree con los elementos
      for s in range (n * 10 ** 5):
        m = Mbr(2 ** d)
        m.setPoint([random.random() for _ in range(2 ** d)])
        mTree.insert(m)
      f.write("%d %d %f %f %f %f\n" % (mTree.d, n * 10 ** 5, mTree.getMeanNodePartitions(), mTree.meanInsertionTime, mTree.meanTotalNodes, mTree.meanInternalNodes))
      f.write("d n meanVisited meanQueryTime\n")
      # Construyo los elementos de consulta
      for s in range (n * 10 ** 3):
        obj = [random.random() for _ in range(2 ** d)]
        for radio in [0.01, 0.10, 0.25, 0.50, 0.75, 0.90, 0.99]:
          mTree.search(radio * (d ** 0.5), obj)
      f.write("%d %d %f %f\n" % (mTree.d, n * 10 ** 3, mTree.computeMeanNodes(), mTree.meanSearchTime))
          
  pass
