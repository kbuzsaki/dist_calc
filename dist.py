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

def align_column(column):
    max_val_len = max(len(v) for v in column)
    spaces = lambda v: " " * (max_val_len - len(str(v)))
    return [v + spaces(v) for v in column]


def align_rows(rows):
    columns = zip(*rows)
    aligned_cols = [align_column(col) for col in columns]
    return zip(*aligned_cols)

class Dist:

    def __init__(self, buckets):
        self._buckets = list(sorted(buckets))

    @staticmethod
    def zero():
        return Dist([(0, 1)])

    @staticmethod
    def uniform(r):
        return Dist([(v, 1) for v in r])

    @staticmethod
    def d(n):
        return Dist.uniform(range(1, n + 1))

    def __repr__(self):
        return "Dist(" + repr(self._buckets) + ")"

    def __str__(self, c_formatters=None):
        if not c_formatters:
            c_formatters = [format_c]
        rows = [[str(v) + ":"] + [f(c) for f in c_formatters] for v, c in self._buckets]
        return "\n".join(" ".join(row) for row in align_rows(rows))

    def __len__(self):
        return round(sum(c for v, c in self._buckets))

    def __iter__(self):
        for v, c in self._buckets:
            for _ in range(c):
                yield v

    def __getitem__(self, index):
        if type(index) != int:
            raise Exception("Can't index with type: " + str(type(index)))
        if index < 0 or index > len(self):
            raise Exception("Index out of bounds: " + str(index))
        cursor = 0
        for (v, c) in self._buckets:
            cursor += c
            if index < cursor:
                return v

    def _project(self, f):
        """ Projects this distribution into a new distribution by applying the
            function f to each bucket's value to find the corresponding
            "projected" bucket and adding the original bucket's count to the
            projected bucket's count.
        """
        combined = Counter()
        for (v, c) in self._buckets:
            combined[f(v)] += c
        return Dist(combined.items())

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
    __radd__ = __add__

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
    __rmul__ = __mul__

    def advantage(self, other=None):
        if not other:
            other = self
        return self._combine(other, max)

    def disadvantage(self, other=None):
        if not other:
            other = self
        return self._combine(other, min)

    def round_down(self):
        return self._project(math.floor)

    def round_up(self):
        return self._project(math.ceil)

    def pass_fail(self, threshold, pass_val=1, fail_val=0):
        return self._project(lambda v: pass_val if v >= threshold else fail_val)

    def mean(self):
        total = 0
        for v, c in self._buckets:
            total += v * c
        return total / len(self)

    def variance(self):
        mean = self.mean()
        return sum((mean - v)**2 * c for v, c in self._buckets) / len(self)

    def stdev(self):
        return math.sqrt(self.variance())

    def median(self):
        midpoint = (len(self) - 1) / 2
        upper_midpoint = math.ceil(midpoint)
        lower_midpoint = math.floor(midpoint)
        return (self[upper_midpoint] + self[lower_midpoint]) / 2

    def summary(self):
        mean = self.mean()
        stdev = self.stdev()
        median = self.median()
        return "\n".join(["mean: {:.2f}, stdev: {:.2f}, median: {:.2f}".format(mean, stdev, median),
                "within 1 stdev (68%): {:.2f} - {:.2f}".format(mean - stdev, mean + stdev),
                "within 2 stdev (95%): {:.2f} - {:.2f}".format(mean - 2*stdev, mean + 2*stdev),
                ])

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

    def _graph(self, columns=None, extra_detail=None):
        if not columns:
            columns = 20
        max_c = max(c for v, c in self._buckets)
        cell_size = max_c / columns
        graph_format = lambda c : math.floor(c / cell_size) * "#"

        if extra_detail:
            formatters = [extra_detail, graph_format]
        else:
            formatters = [graph_format]

        return self.__str__(formatters) + "\neach # represents {:.2f}".format(cell_size)

    def graph(self, columns=None):
        return self._graph(columns, extra_detail=lambda c: "({:.2f})".format(c))

    def details(self, columns=None):
        return self.graph(columns) + "\n" + self.summary() + "\n"

coin = Dist.uniform(range(2))
d2 = Dist.d(2)
d4 = Dist.d(4)
d6 = Dist.d(6)
d8 = Dist.d(8)
d10 = Dist.d(10)
d12 = Dist.d(12)
d20 = Dist.d(20)

