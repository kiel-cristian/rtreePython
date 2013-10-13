# encoding: utf-8
import random

class SortingManager():
  def quicksort(self, compare, elements):
    self.cost = 0
    return self.quicksortI(compare, elements)

  def mergesort(self, compare, elements):
    self.cost = 0
    return self.mergesortI(compare, elements)

  def getCost(self):
    return self.cost

  # compare(a,b): funcion que retorna -1, 0, 1 si a es menor, igual, o mayer que b respectivamente
  def quicksortI(self, compare, elements):
    l = len(elements)
    if l <= 1:
      return elements

    pivot = elements[int(random.random() * l)]

    firstPartition  = []
    secondPartition = []

    for e in elements:
      self.cost = self.cost + 1
      if compare(e, pivot) <= 0:
        firstPartition  = firstPartition  + [e]
      else:
        secondPartition = secondPartition + [e]

    return self.quicksortI(compare, firstPartition) + self.quicksortI(compare, secondPartition)

  def mergesortI(self, compare, elements):
    l = len(elements)
    if l<= 1:
      return elements
    elif l == 2:
      self.cost = self.cost + 1
      if compare(elements[0], elements[1]) <= 0:
        return elements
      else:
        return [elements[1]] + [elements[0]]

    div = l/2
    random.shuffle(elements)
    self.cost = self.cost + div

    firstPartition  = self.mergesortI(compare, elements[0:div])
    secondPartition = self.mergesortI(compare, elements[div:])

    # merge
    merge = []
    fl = div
    sl = l - div

    while fl or sl > 0:
      if fl > 0 and sl > 0:
        self.cost = self.cost + 1
        if compare(firstPartition[0], secondPartition[0]) < 0:
          merge = merge + [firstPartition[0]]
          firstPartition = firstPartition[1:]
          fl = fl -1
        else:
          merge = merge + [secondPartition[0]]
          secondPartition = secondPartition[1:]
          sl = sl -1
      elif fl > 0:
        merge = merge + firstPartition
        break
      elif sl > 0:
        merge = merge + secondPartition
        break
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
  print(sm.getCost())
  print(sm.mergesort(cList, a))
  print(sm.getCost())
  print(a)

  print(sm.quicksort(cList, [2,1]))
  print(sm.getCost())
  print(sm.mergesort(cList, [2,1]))
  print(sm.getCost())
