# encoding: utf-8
from random import random

class SortingManager():
  # compare(a,b): funcion que retorna -1, 0, 1 si a es menor, igual, o mayer que b respectivamente
  def quicksort(self, compare, elements):
    l = len(elements)
    if l <= 1:
      return elements

    pivot = elements[int(random() * l)]

    firstPartition  = [_ for _ in elements if compare(_, pivot) <= 0] # elementos menores o iguales que pivot
    secondPartition = [_ for _ in elements if compare(_, pivot) > 0]  # elementos mayores que el pivote

    return self.quicksort(compare, firstPartition) + self.quicksort(compare, secondPartition)

  def mergesort(self, compare, elements):
    l = len(elements)
    if l<= 1:
      return elements
    elif l == 2:
      if compare(elements[0], elements[1]) < 0:
        return elements
      else:
        [elements[1]] + [elements[0]]

    div = l/2
    firstPartition  = self.mergesort(compare, elements[0:div])
    secondPartition = self.mergesort(compare, elements[div:])

    # merge
    merge = []
    fl = div
    sl = l - div

    if fl < sl:
      minl = fl
    else:
      minl = sl

    for i in range(minl):
      if compare(firstPartition[0], secondPartition[0]) < 0:
        merge = merge + [firstPartition[0]]
        firstPartition = firstPartition[1:]
      else:
        merge = merge + [secondPartition[0]]
        secondPartition = secondPartition[1:]

    if len(firstPartition) > 0:
      merge = merge + firstPartition
    if len(secondPartition) > 0:
      merge = merge + secondPartition

    return merge

if __name__ == "__main__":

  def cList(x,y):
    if x < y:
      return -1
    elif x > y:
      return 1
    else:
      return 0

  sm = SortingManager()
  a = [1,2,3,4,5,6,0]
  
  print(sm.quicksort(cList, a))
  print(sm.mergesort(cList, a))
  print(a)

  print(sm.quicksort(cList, [2,1]))
  print(sm.mergesort(cList, [2,1]))
