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
    def exactly(value):
        return Dist.uniform([value])

    @staticmethod
    def d(n):
        return Dist.uniform(range(1, n + 1))

    @staticmethod
    def from_lines(lines):
        return Dist(Counter(int(float(line)) for line in lines.split()).items())

    def __repr__(self):
        f = lambda v: str(v) if v == int(v) else "{:0.4f}".format(v).rstrip("0").rstrip(".")
        return "Dist([" + ", ".join("(" + str(k) + ", " + f(v) + ")" for k, v in self._buckets) + "])"

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

    def values(self):
        return [v for (v, c) in self._buckets]

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

    def __sub__(self, other):
        if type(other) == Dist:
            return self._combine(other, operator.sub)
        else:
            return Dist([(v - other, c) for v, c in self._buckets])

    def __rsub__(self, other):
        if type(other) == Dist:
            return other._combine(self, operator.sub)
        else:
            return Dist([(other - v, c) for v, c in self._buckets])

    def __mul__(self, other):
        """ Multiplies the *buckets* of this distribution by other. Kind of.

            The true purpose is to make "2d6" easy to express as "2 * d6".
            For example, 2 * d3 = d3 + d3 = [2, 3, 4, 5, 6]
        """
        if type(other) == int:
            output = Dist.zero()
            for i in range(other):
                output += self
            return output
        elif type(other) == Dist:
            return self._combine(other, operator.mul)
        else:
            raise Exception("unknown type: " + repr(other))
    __rmul__ = __mul__

    def scale(self, other):
        """ Multiplies the *values* of this distribution by other.

            This is arguably the more natural interpretation of what "multiplication" by a number
            should do, but it's a less common operation in D&D so it gets the more obscure name.
            For example, d3.scale(2) = [2, 4, 6]
        """
        if type(other) == Dist:
            raise Exception("Can't scale a distribution by another distribution!")
        else:
            return Dist([(v * other, c) for v, c in self._buckets])

    def vector_add(self, other):
        """ Sums the two distributions directly, rather than combining probabalistically.

            This is in contrast with __add__ which simulates "rolling the dice" for each distribution.
        """
        return Dist((Counter(dict(self._buckets)) + Counter(dict(other._buckets))).items())

    def __truediv__(self, other):
        if type(other) == Dist:
            raise Exception("Can't divide a distribution by another distribution!")
        else:
            return Dist([(v / other, c) for v, c in self._buckets])

    def __rtruediv__(self, other):
        if type(other) == Dist:
            raise Exception("Can't divide a distribution by another distribution!")
        else:
            return Dist([(other / v, c) for v, c in self._buckets])

    def truncate(self, allowed_range):
        return Dist([(v, c) for v, c in self._buckets if v in allowed_range])

    def clamp(self, allowed_range):
        def clamp_to_range(value):
            if value < allowed_range.start:
                return allowed_range.start
            elif value > allowed_range.stop:
                return allowed_range.stop
            else:
                return value
        return self._project(clamp_to_range)

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

    def round_awars(self):
        """ Advance wars rounds 0.95 and higher up, but otherwise rounds down. """
        def awars_round(n):
            fractional = n - math.floor(n)
            if fractional >= 0.95:
                return math.ceil(n)
            return math.floor(n)
        return self._project(awars_round)

    def pass_fail(self, threshold, force_fail=1, pass_val=1, fail_val=0):
        return self._project(lambda v: pass_val if v >= threshold and v > force_fail else fail_val)

    def transform(self, f):
        return self._project(f)

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
        total_count = sum(c for _, c in self._buckets)
        partial_count = 0
        thresh = total_count / 2
        min_val = None
        # TODO: make this less janky? it's this way to handle normalized distributions
        for v, c in self._buckets:
            if min_val is not None:
                max_val = v
                break
            partial_count += c
            if partial_count > thresh:
                return v
            elif partial_count == thresh:
                min_val = v
                max_val = v
        return (min_val + max_val) / 2

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
        if length == 0:
            return self
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

        return self.__str__(formatters) + "\neach # represents {:.4f}".format(cell_size)

    def graph(self, columns=None):
        return self._graph(columns, extra_detail=lambda c: "({:.4f})".format(c))

    def details(self, columns=None):
        return self.graph(columns) + "\n" + self.summary() + "\n"

def details(d):
    print(d.details())

def cdf_details(d):
    print(d.to_cdf().details())

def rcdf_details(d):
    print(d.to_rcdf().details())

coin = Dist.uniform(range(2))
d2 = Dist.d(2)
d4 = Dist.d(4)
d6 = Dist.d(6)
d8 = Dist.d(8)
d10 = Dist.d(10)
d12 = Dist.d(12)
d20 = Dist.d(20)

