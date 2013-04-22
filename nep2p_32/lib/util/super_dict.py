import random

__all__ = ['SuperDict']

class SuperDict:
    def __init__(self, maxScore=1000):
        self.realDict = {}
        self.sortedList = []
        self.maxScore = maxScore
        self.sortedNum = 0
        self.dirty = False

    def __contains__(self, key):
        return key in self.realDict

    def __len__(self):
        return len(self.realDict)

    def iteritems(self):
        return self.realDict.iteritems()

    def __getitem__(self, key):
        return self.realDict[key]

    def __setitem__(self, key, value):
        if 0 <= value and value <= self.maxScore:
            self.realDict[key] = value
            self.dirty = True

    def __delitem__(self, key):
        del self.realDict[key]

    def getList(self, num=None):
        if num == None:
            num = len(self.realDict)
        if self.dirty or num > self.sortedNum:
            self._sort(num)
        return self.sortedList[:num]

    def _sort(self, num):
        tempList = []
        tempSorted = 0
        finished = False
        countArray = [[] for i in xrange(self.maxScore)]

        for key, value in self.realDict.iteritems():
            countArray[value].append(key)

        for i in reversed(xrange(self.maxScore)):
            if finished:
                break
            for j in countArray[i]:
                tempList.append((j, i))
                tempSorted += 1
                if tempSorted == num:
                    finished = True
                    break

        self.sortedList = tempList
        self.sortedNum = num
        self.dirty = False

if __name__ == "__main__":
    s = SuperDict(256)
    for i in xrange(500000):
        s['key%d' % i] = random.randint(0, 255)
    for i in xrange(400):
        del s['key%d' % i]
    #l1 = s.getList()
    #l2 = s.getList(1000)
    print s.getList(50)
