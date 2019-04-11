from math import log, ceil, floor

class VanEmdeBoasTree:
    """
    Van Emde Boas Tree.
    """

    def __init__(self, valueRange):
        """
        Generates an empty veb-tree with the given
        range.
        """
        bitSize = ceil(log(valueRange, 2))
        self.valueRange =  1 << bitSize
        self.min = None
        self.max = None
        if self.valueRange > 2:
            halfBitSize = bitSize/2

            self.summary = None
            self.cluster = dict()
            self.lsbSize = floor(halfBitSize)
            self.lsqrt = 1 << self.lsbSize
            self.hsqrt = 1 << ceil(halfBitSize) 
            self.lsbMask = self.lsqrt - 1


    def clusterIndex(self, x):
        """
        Returns the index of the cluster holding x.
        """
        return x >> self.lsbSize 


    def valueIndex(self, x):
        """
        Returns the index of x inside its cluster.
        """
        return x & self.lsbMask 


    def value(self, clusterIndex, valueIndex):
        """
        Returns the value associated with the pair
        (clusterIndex, valueIndex).
        """
        return (clusterIndex << self.lsbSize) + valueIndex


    def contains(self, x):
        """
        Checks whether x is present in the veb-tree.
        """
        if self.min == x or self.max == x:
            return True

        if self.min == None or x < self.min or x > self.max or self.valueRange == 2:
            return False

        xCluster = self.cluster.get(self.clusterIndex(x), None)
        return (xCluster != None) and xCluster.contains(self.valueIndex(x))


    def predecessor(self, x):
        """
        Returns the predecessor of x in the veb-tree.
        """
        if self.valueRange == 2:
            return 0 if (x == 1 and self.min == 0) else None

        if self.max != None and x > self.max:
            return self.max

        xClusterIndex = self.clusterIndex(x)
        xCluster = self.cluster.get(xClusterIndex, None)
        xIndex = self.valueIndex(x)

        if xCluster != None and xCluster.min < xIndex:
            return self.value(xClusterIndex, xCluster.predecessor(xIndex))

        if self.summary != None:
            predClusterIndex = self.summary.predecessor(xClusterIndex)
            if predClusterIndex != None:
                return self.value(predClusterIndex, self.cluster[predClusterIndex].max)

        return self.min if (self.min != None and x > self.min) else None


    def successor(self, x):
        """
        Returns the successor of x in the veb-tree.
        """
        if self.valueRange == 2:
            return 1 if (x == 0 and self.max == 1) else None

        if self.min != None and x < self.min:
            return self.min

        xClusterIndex = self.clusterIndex(x)
        xCluster = self.cluster.get(xClusterIndex, None)
        xIndex = self.valueIndex(x)

        if xCluster != None and xCluster.max > xIndex:
            return self.value(xClusterIndex, xCluster.successor(xIndex))

        if self.summary != None:
            succClusterIndex = self.summary.successor(xClusterIndex)
            if succClusterIndex != None:
                return self.value(succClusterIndex, self.cluster[succClusterIndex].min)
        
        return self.max if (self.max != None and x < self.max) else None 


    def insert(self, x):
        """
        Inserts value x into the veb-tree.
        """
        if x == self.min or x == self.max:
            return

        if self.min == None:
            self.min = self.max = x
            return

        if self.min == self.max:
            if x < self.min:
                self.min = x
            elif x > self.max:
                self.max = x
            return

        if self.valueRange == 2:
            return

        if x < self.min:
            self.min, x = x, self.min

        elif x > self.max:
            self.max, x = x, self.max

        xClusterIndex = self.clusterIndex(x)
        xCluster = self.cluster.get(xClusterIndex, None)
        xIndex = self.valueIndex(x)

        if xCluster == None:
            if self.summary == None:
                self.summary = VanEmdeBoasTree(self.hsqrt)
            self.summary.insert(xClusterIndex)

            xCluster = VanEmdeBoasTree(self.lsqrt)
            self.cluster[xClusterIndex] = xCluster

        xCluster.insert(xIndex)


    def delete(self, x):
        """
        Deletes x from the veb-tree.
        """
        if self.min == None or x < self.min or x > self.max:
            return

        if self.min == self.max:
            self.min = self.max = None
            return

        if self.valueRange == 2:
            if x == 0:
                self.min = 1
            else:
                self.max = 0
            return

        if x == self.min:
            if self.summary == None:
                self.min = self.max
                return

            xClusterIndex = self.summary.min
            xCluster = self.cluster[xClusterIndex]
            xIndex = xCluster.min

            self.min = self.value(xClusterIndex, xIndex)

        elif x == self.max:
            if self.summary == None:
                self.max = self.min
                return

            xClusterIndex = self.summary.max
            xCluster = self.cluster[xClusterIndex]
            xIndex = xCluster.max

            self.max = self.value(xClusterIndex, xIndex)

        else:
            xClusterIndex = self.clusterIndex(x)
            xCluster = self.cluster.get(xClusterIndex, None)
            xIndex = self.valueIndex(x)
            if xCluster == None:
                return

        xCluster.delete(xIndex)

        if xCluster.min == None:
            del self.cluster[xClusterIndex]
            self.summary.delete(xClusterIndex)

            if self.summary.min == None:
                self.summary = None


    def __iter__(self):
        """
        Iterator over the elements in the veb-tree.
        """
        value = self.min
        while value != None:
            yield value 
            value = self.successor(value)


    def __str__(self):
        """
        Returns a string representing the veb-tree.
        """
        return str(tuple(value for value in self))


    def __repr__(self):
        """
        Represents the veb-tree.
        """
        return str(self)

