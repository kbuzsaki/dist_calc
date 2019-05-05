from collections import Counter
import statistics

class Dist:

    def __init__(self, buckets):
        self._buckets = list(sorted(buckets))

    @staticmethod
    def zero():
        return Dist([(0, 1)])

    @staticmethod
    def uniform(r):
        return Dist([(v, 1) for v in r])

    def __repr__(self):
        return "Dist(" + repr(self._buckets) + ")"

    def __str__(self):
        return "\n".join(str(p[0]) + ": " + str(p[1]) for p in self._buckets)

    def __len__(self):
        return sum(c for v, c in self._buckets)

    def __iter__(self):
        for v, c in self._buckets:
            for _ in range(c):
                yield v

    def __add__(self, other):
        if type(other) == Dist:
            combined = Counter()
            for (v1, c1) in self._buckets:
                for (v2, c2) in other._buckets:
                    combined[v1 + v2] += c1 * c2
            return Dist(combined.items())
        else:
            return Dist([(v + other, c) for v, c in self._buckets])

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if type(other) == int:
            output = Dist.zero()
            for i in range(other):
                output += self
            return output
        elif type(other) == Dist:
            combined = Counter()
            for (v1, c1) in self._buckets:
                for (v2, c2) in other._buckets:
                    combined[v1 * v2] += c1 * c2
            return Dist(combined.items())
        else:
            raise Exception("unknown type")

    def __rmul__(self, other):
        return self.__mul__(other)

coin = Dist.uniform(range(2))
d2 = Dist.uniform(range(1, 3))
d4 = Dist.uniform(range(1, 5))
d6 = Dist.uniform(range(1, 7))
d8 = Dist.uniform(range(1, 9))
d10 = Dist.uniform(range(1, 11))
d12 = Dist.uniform(range(1, 13))
d20 = Dist.uniform(range(1, 21))

