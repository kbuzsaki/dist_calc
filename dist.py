import math
import operator
from collections import Counter
import statistics

# garbage formatting only print the decimals if necessary
def format_c(c):
    initial = ('%.3f' % c)
    if "." in initial:
        while initial[-1] == "0":
            initial = initial[:-1]
        if initial[-1] == ".":
            initial = initial[:-1]
    return initial


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
        return "\n".join(str(v) + ": " + format_c(c) for v, c in self._buckets)

    def __len__(self):
        return sum(c for v, c in self._buckets)

    def __iter__(self):
        for v, c in self._buckets:
            for _ in range(c):
                yield v

    def _combine(self, other, f):
        combined = Counter()
        for (v1, c1) in self._buckets:
            for (v2, c2) in other._buckets:
                new_val = f(v1, v2)
                combined[new_val] += c1 * c2
        return Dist(combined.items())


    def __add__(self, other):
        if type(other) == Dist:
            return self._combine(other, operator.add)
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
            return self._combine(other, operator.mul)
        else:
            raise Exception("unknown type")

    def __rmul__(self, other):
        return self.__mul__(other)

    def advantage(self, other=None):
        if not other:
            other = self
        return self._combine(other, max)

    def disadvantage(self, other=None):
        if not other:
            other = self
        return self._combine(other, min)

    def mean(self):
        total = 0
        for v, c in self._buckets:
            total += v * c
        return total / len(self)

    def normalize(self):
        length = len(self)
        return Dist([(v, c / length) for v, c in self._buckets])

    def to_cdf(self):
        norm = self.normalize()
        buckets = []
        cum_c = 0
        for v, c in norm._buckets:
            cum_c += c
            buckets.append((v, cum_c))
        return Dist(buckets)

    def to_rcdf(self):
        norm = self.normalize()
        buckets = []
        cum_c = 0
        for v, c in reversed(norm._buckets):
            cum_c += c
            buckets.append((v, cum_c))
        return Dist(buckets)

    def round_down(self):
        combined = Counter()
        for (v1, c1) in self._buckets:
            combined[math.floor(v1)] += c1
        return Dist(combined.items())

    def round_up(self):
        combined = Counter()
        for (v1, c1) in self._buckets:
            combined[math.ceil(v1)] += c1
        return Dist(combined.items())

    def pass_fail(self, threshold, pass_val=1, fail_val=0):
        count_pass = sum(c for v, c in self._buckets if v >= threshold)
        count_fail = len(self) - count_pass
        return Dist([(pass_val, count_pass), (fail_val, count_fail)])

coin = Dist.uniform(range(2))
d2 = Dist.uniform(range(1, 3))
d4 = Dist.uniform(range(1, 5))
d6 = Dist.uniform(range(1, 7))
d8 = Dist.uniform(range(1, 9))
d10 = Dist.uniform(range(1, 11))
d12 = Dist.uniform(range(1, 13))
d20 = Dist.uniform(range(1, 21))

