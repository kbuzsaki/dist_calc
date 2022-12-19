from dist import *

from collections import namedtuple
from enum import Enum, unique
import inspect
import sys

debug = False
def debug_log(*args, **kwargs):
    if debug:
        print(*args, **kwargs)

@unique
class MoveType(Enum):
    T = "Treads"
    A = "Air"
    S = "Ship"
    L = "Lander"
    F = "Foot"
    B = "Boot"
    W = "Wheels"
    P = "Piperunner"


@unique
class TerrainType(Enum):
    plains = 1
    mountain = 2
    forest = 3
    river = 4
    road = 5
    bridge = 6
    ocean = 7
    shoal = 8
    reef = 9
    city = 10
    base = 11
    airport = 12
    port = 13
    hq = 14
    pipe = 15
    silo = 16
    com_tower = 17
    lab = 18

    @property
    def data(self):
        return TERRAIN_DATA_MAP[self]

    @property
    def is_urban(self):
        return self in {TerrainType.city, TerrainType.base, TerrainType.airport,
                        TerrainType.port, TerrainType.hq, TerrainType.com_tower, TerrainType.lab}

TerrainData = namedtuple("TerrainData", ["type", "name", "defense"])

TERRAIN_DATAS = [
    TerrainData(TerrainType.plains, "Plains", 1),
    TerrainData(TerrainType.mountain, "Mountain", 4),
    TerrainData(TerrainType.forest, "Forest", 2),
    TerrainData(TerrainType.river, "River", 0),
    TerrainData(TerrainType.road, "Road", 0),
    TerrainData(TerrainType.bridge, "Bridge", 0),
    TerrainData(TerrainType.ocean, "Ocean", 0),
    TerrainData(TerrainType.shoal, "Shoal", 0),
    TerrainData(TerrainType.reef, "Reef", 1),
    TerrainData(TerrainType.city, "City", 3),
    TerrainData(TerrainType.base, "Base", 3),
    TerrainData(TerrainType.airport, "Airport", 3),
    TerrainData(TerrainType.port, "Port", 3),
    TerrainData(TerrainType.hq, "HQ", 4),
    TerrainData(TerrainType.pipe, "Pipe", 0),
    TerrainData(TerrainType.silo, "Silo", 3),
    TerrainData(TerrainType.com_tower, "Com. Tower", 3),
    TerrainData(TerrainType.lab, "Lab", 3),
]
TERRAIN_DATA_MAP = {data.type: data for data in TERRAIN_DATAS}

# Convenience Variables
plains = TERRAIN_DATA_MAP[TerrainType.plains]
mountain = TERRAIN_DATA_MAP[TerrainType.mountain]
forest = TERRAIN_DATA_MAP[TerrainType.forest]
river = TERRAIN_DATA_MAP[TerrainType.river]
road = TERRAIN_DATA_MAP[TerrainType.road]
bridge = TERRAIN_DATA_MAP[TerrainType.bridge]
ocean = TERRAIN_DATA_MAP[TerrainType.ocean]
shoal = TERRAIN_DATA_MAP[TerrainType.shoal]
reef = TERRAIN_DATA_MAP[TerrainType.reef]
city = TERRAIN_DATA_MAP[TerrainType.city]
base = TERRAIN_DATA_MAP[TerrainType.base]
airport = TERRAIN_DATA_MAP[TerrainType.airport]
port = TERRAIN_DATA_MAP[TerrainType.port]
hq = TERRAIN_DATA_MAP[TerrainType.hq]
pipe = TERRAIN_DATA_MAP[TerrainType.pipe]
silo = TERRAIN_DATA_MAP[TerrainType.silo]
com_tower = TERRAIN_DATA_MAP[TerrainType.com_tower]
lab = TERRAIN_DATA_MAP[TerrainType.lab]


@unique
class UnitType(Enum):
    anti_air = 1
    apc = 2
    artillery = 3
    bcopter = 4
    battleship = 5
    black_boat = 6
    black_bomb = 7
    bomber = 8
    carrier = 9
    cruiser = 10
    fighter = 11
    infantry = 12
    lander = 13
    md_tank = 14
    mech = 15
    mega_tank = 16
    missile = 17
    neotank = 18
    piperunner = 19
    recon = 20
    rocket = 21
    stealth = 22
    sub = 23
    tcopter = 24
    tank = 25

    @property
    def data(self):
        return UNIT_DATA_MAP[self]

    @property
    def is_air(self):
        return self.data.move_type == MoveType.A

    @property
    def is_sea(self):
        return self.data.move_type in {MoveType.S, MoveType.L}

    @property
    def is_infantry(self):
        return self in {UnitType.infantry, UnitType.mech}

    @property
    def is_vehicle(self):
        return self.data.move_type in {MoveType.T, MoveType.W, MoveType.P}

    @property
    def is_copter(self):
        return self in {UnitType.bcopter, UnitType.tcopter}

    @property
    def is_indirect(self):
        return self in {
                UnitType.artillery, UnitType.rocket, UnitType.missile,
                UnitType.piperunner, UnitType.battleship, UnitType.carrier,
        }

    @property
    def is_direct(self):
        return not self.is_indirect


UnitData = namedtuple("UnitData",
        ["type", "name", "move", "ammo", "fuel", "fuel_use", "vision", "min_range", "max_range", "move_type", "cost"])

UNIT_DATAS = [
    UnitData(UnitType.anti_air, "Anti-Air", 6, 9, 60, 0, 2, 0, 0, MoveType.T, 8000),
    UnitData(UnitType.apc, "APC", 6, 0, 70, 0, 1, 0, 0, MoveType.T, 5000),
    UnitData(UnitType.artillery, "Artillery", 5, 9, 50, 0, 1, 2, 3, MoveType.T, 6000),
    UnitData(UnitType.bcopter, "B-Copter", 6, 6, 99, 2, 3, 0, 0, MoveType.A, 9000),
    UnitData(UnitType.battleship, "Battleship", 5, 9, 99, 1, 2, 2, 6, MoveType.S, 28000),
    UnitData(UnitType.black_boat, "Black Boat", 7, 0, 60, 1, 1, 0, 0, MoveType.L, 7500),
    UnitData(UnitType.black_bomb, "Black Bomb", 9, 0, 45, 5, 1, 0, 0, MoveType.A, 25000),
    UnitData(UnitType.bomber, "Bomber", 7, 9, 99, 5, 2, 0, 0, MoveType.A, 22000),
    UnitData(UnitType.carrier, "Carrier", 5, 9, 99, 1, 4, 3, 8, MoveType.S, 30000),
    UnitData(UnitType.cruiser, "Cruiser", 6, 9, 99, 1, 3, 0, 0, MoveType.S, 18000),
    UnitData(UnitType.fighter, "Fighter", 9, 9, 99, 5, 2, 0, 0, MoveType.A, 20000),
    UnitData(UnitType.infantry, "Infantry", 3, 0, 99, 0, 2, 0, 0, MoveType.F, 1000),
    UnitData(UnitType.lander, "Lander", 6, 0, 99, 1, 1, 0, 0, MoveType.L, 12000),
    UnitData(UnitType.md_tank, "Md.Tank", 5, 8, 50, 0, 1, 0, 0, MoveType.T, 16000),
    UnitData(UnitType.mech, "Mech", 2, 3, 70, 0, 2, 0, 0, MoveType.B, 3000),
    UnitData(UnitType.mega_tank, "Mega Tank", 4, 3, 50, 0, 1, 0, 0, MoveType.T, 28000),
    UnitData(UnitType.missile, "Missile", 4, 6, 50, 0, 5, 3, 5, MoveType.W, 12000),
    UnitData(UnitType.neotank, "Neotank", 6, 9, 99, 1, 1, 0, 0, MoveType.T, 22000),
    UnitData(UnitType.piperunner, "Piperunner", 9, 9, 99, 0, 4, 2, 5, MoveType.P, 20000),
    UnitData(UnitType.recon, "Recon", 8, 0, 80, 0, 5, 0, 0, MoveType.W, 4000),
    UnitData(UnitType.rocket, "Rocket", 5, 6, 50, 0, 1, 3, 5, MoveType.W, 15000),
    UnitData(UnitType.stealth, "Stealth", 6, 6, 60, 5, 4, 0, 0, MoveType.A, 24000),
    UnitData(UnitType.sub, "Sub", 5, 6, 60, 1, 5, 0, 0, MoveType.S, 20000),
    UnitData(UnitType.tcopter, "T-Copter", 6, 0, 99, 2, 2, 0, 0, MoveType.A, 5000),
    UnitData(UnitType.tank, "Tank", 6, 9, 70, 0, 3, 0, 0, MoveType.T, 7000),
]
UNIT_DATA_MAP = {data.type: data for data in UNIT_DATAS}

# Index is UnitType.value - 1
DAMAGE_MATRIX = [
    [45, 50, 50, 120, 0, 0, 120, 75, 0, 0, 65, 105, 0, 10, 105, 1, 55, 5, 25, 60, 55, 75, 0, 120, 25],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [75, 70, 75, 0, 40, 55, 0, 0, 45, 65, 0, 90, 55, 45, 85, 15, 80, 40, 70, 80, 80, 0, 60, 0, 70],
    [25, 60, 65, 65, 25, 25, 0, 0, 25, 55, 0, 75, 25, 25, 75, 10, 65, 20, 55, 55, 65, 0, 25, 95, 55],
    [85, 80, 80, 0, 50, 95, 0, 0, 60, 95, 0, 95, 95, 55, 90, 25, 90, 50, 80, 90, 85, 0, 95, 0, 80],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [95, 105, 105, 0, 75, 95, 0, 0, 75, 85, 0, 110, 95, 95, 110, 35, 105, 90, 105, 105, 105, 0, 95, 0, 105],
    [0, 0, 0, 115, 0, 0, 120, 100, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 115, 0],
    [0, 0, 0, 115, 0, 25, 120, 65, 5, 0, 55, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 90, 115, 0],
    [0, 0, 0, 100, 0, 0, 120, 100, 0, 0, 55, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 85, 0, 100, 0],
    [5, 14, 15, 7, 0, 0, 0, 0, 0, 0, 0, 55, 0, 1, 45, 1, 26, 1, 5, 12, 25, 0, 0, 30, 5],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [105, 105, 105, 12, 10, 35, 0, 0, 10, 45, 0, 105, 35, 55, 95, 25, 105, 45, 85, 105, 105, 0, 10, 45, 85],
    [65, 75, 70, 9, 0, 0, 0, 0, 0, 0, 0, 65, 0, 15, 55, 5, 85, 15, 55, 85, 85, 0, 0, 35, 55],
    [195, 195, 195, 22, 45, 105, 0, 0, 45, 65, 0, 135, 75, 125, 125, 65, 195, 115, 180, 195, 195, 0, 45, 55, 180],
    [0, 0, 0, 120, 0, 0, 120, 100, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 120, 0],
    [115, 125, 115, 22, 15, 40, 0, 0, 15, 50, 0, 125, 50, 75, 115, 35, 125, 55, 105, 125, 125, 0, 15, 55, 105],
    [85, 80, 80, 105, 55, 60, 120, 75, 60, 85, 65, 95, 60, 55, 90, 25, 90, 50, 80, 90, 85, 75, 85, 105, 80],
    [4, 45, 45, 12, 0, 0, 0, 0, 0, 0, 0, 70, 0, 1, 65, 1, 28, 1, 6, 35, 55, 0, 0, 35, 6],
    [85, 80, 80, 0, 55, 60, 0, 0, 60, 85, 0, 95, 60, 55, 90, 25, 90, 50, 80, 90, 85, 0, 85, 0, 80],
    [50, 85, 75, 85, 45, 65, 120, 70, 45, 35, 45, 90, 65, 70, 90, 15, 85, 60, 80, 85, 85, 55, 55, 95, 75],
    [0, 0, 0, 0, 55, 95, 0, 0, 75, 25, 0, 0, 95, 0, 0, 0, 0, 0, 0, 0, 0, 0, 55, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [65, 75, 70, 10, 1, 10, 0, 0, 1, 5, 0, 75, 10, 15, 70, 10, 85, 15, 55, 85, 85, 0, 1, 40, 55]
]


@unique
class PowerType(Enum):
    no_power = 1
    cop = 2
    scop = 3

    @property
    def char(self):
        if self == PowerType.no_power:
            return "N"
        elif self == PowerType.cop:
            return "Y"
        else:
            return "S"

no_power = PowerType.no_power
cop = PowerType.cop
scop = PowerType.scop


@unique
class CoType(Enum):
    adder = 1
    andy = 2
    colin = 3
    drake = 4
    eagle = 5
    flak = 6
    grimm = 7
    grit = 8
    hachi = 9
    hawke = 10
    jake = 11
    javier = 12
    jess = 13
    jugger = 14
    kanbei = 15
    kindle = 16
    koal = 17
    lash = 18
    max = 19
    nell = 20
    olaf = 21
    rachel = 22
    sami = 23
    sasha = 24
    sensei = 25
    sonja = 26
    sturm = 27
    von_bolt = 28

STANDARD_LUCK = Dist.d(10) - 1
SONJA_LUCK = STANDARD_LUCK - STANDARD_LUCK
NELL_LUCK = Dist.d(20) - 1
RACHEL_LUCK = Dist.d(40) - 1

STANDARD_STATS = lambda unit: (100, 100)
STANDARD_BOOST = lambda unit: (10, 10)
TOWERS = 1
DTOWERS = 1


def invoke_with_desired_args(f, args):
    spec = inspect.getfullargspec(f)
    return f(*args[:len(spec.args)])


class CommandingOfficer:

    def __init__(self, t=None, luck=STANDARD_LUCK, stat_override=None, cop_boost=None, scop_boost=None):
        self.towers = t
        self.luck = luck
        self.stat_override = stat_override or STANDARD_STATS
        self.cop_boost = cop_boost or STANDARD_BOOST
        self.scop_boost = scop_boost or self.cop_boost

    def tower_boost(self):
        if self.towers is None:
            return TOWERS * 10
        return self.towers * 10

    def power_boost(self, unit, power, other):
        if power == PowerType.no_power:
            return 0, 0
        elif power == PowerType.cop:
            return invoke_with_desired_args(self.cop_boost, [unit, other])
        elif power == PowerType.scop:
            return invoke_with_desired_args(self.scop_boost, [unit, other])

    def attack_for(self, unit, power, defender):
        base_attack, _ = invoke_with_desired_args(self.stat_override, [unit, defender])
        attack_boost, _ = self.power_boost(unit, power, defender)
        return base_attack + attack_boost + self.tower_boost()

    def defense_for(self, unit, power, attacker):
        _, base_defense = invoke_with_desired_args(self.stat_override, [unit, attacker])
        _, def_boost = self.power_boost(unit, power, attacker)
        return base_defense + def_boost


ATTACKER_POWER = PowerType.no_power
DEFENDER_POWER = PowerType.no_power

def set_meta(*args):
    global TOWERS
    global DTOWERS
    global ATTACKER_POWER
    global DEFENDER_POWER

    int_args = [arg for arg in args if  isinstance(arg, int)]
    power_args = [arg for arg in args if  isinstance(arg, PowerType)]

    TOWERS = int_args[0] if int_args else 1
    DTOWERS = int_args[1] if len(int_args) > 1 else TOWERS

    ATTACKER_POWER = power_args[0] if power_args else no_power
    DEFENDER_POWER = power_args[1] if len(power_args) > 1 else no_power

    sys.ps1 = str(TOWERS) + str(DTOWERS) + ATTACKER_POWER.char + DEFENDER_POWER.char + ">>> "

set_meta(1)

def get_meta():
    return {
        "towers": TOWERS,
        "dtowers": DTOWERS,
        "attacker_power": ATTACKER_POWER,
        "defender_power": DEFENDER_POWER,
    }


def unimplemented(message):
    raise Exception(message)


andy = CommandingOfficer(scop_boost=lambda unit: (20, 10))

colin = CommandingOfficer(
        stat_override=lambda unit: (90, 100),
        scop_boost=lambda unit: unimplemented("Colin SCOP not implemented."))

drake = CommandingOfficer(
        stat_override=lambda unit: (80, 100) if unit.is_air else ((100, 125) if unit.is_sea else (100, 100)))

eagle = CommandingOfficer(
        stat_override=lambda unit: (115, 110) if unit.is_air else ((70, 100) if unit.is_sea else (100, 100)),
        cop_boost=lambda unit: (15, 20) if unit.is_air else (10, 10))

grimm = CommandingOfficer(
        stat_override=lambda unit: (130, 80), cop_boost=lambda unit: (30, 10), scop_boost=lambda unit: (60, 10))

grit = CommandingOfficer(
        stat_override=lambda unit: (120, 100) if unit.is_indirect else ((100, 100) if unit.is_infantry else (80, 100)),
        cop_boost=lambda unit: (30, 10) if unit.is_indirect else (10, 10))

jake = CommandingOfficer(
        stat_override=lambda unit: (110, 100) if unit.terrain == plains else (100, 100),
        cop_boost=lambda unit: (20, 10) if unit.terrain == plains else (10, 10),
        scop_boost=lambda unit: (40, 10) if unit.terrain == plains else (10, 10))

# TODO: use the actual CO's tower value in case of asymmetry?
javier = CommandingOfficer(
        stat_override=lambda unit, other: (100, 100 + 10 * DTOWERS + (20 if other.is_indirect else 0)),
        cop_boost= lambda unit, other: (10 + 10 * TOWERS, 10 + 10 * DTOWERS + (20 if other.is_indirect else 0)),
        scop_boost=lambda unit, other: (10 + 20 * TOWERS, 10 + 20 * DTOWERS + (40 if other.is_indirect else 0)))

jess = CommandingOfficer(
        stat_override=lambda unit: (110, 100) if unit.is_vehicle else (90, 100),
        cop_boost=lambda unit: (20, 10) if unit.is_vehicle else (10, 10),
        scop_boost=lambda unit: (40, 10) if unit.is_vehicle else (10, 10))

# TODO: kanbei scop counterattacks
kanbei = CommandingOfficer(
        stat_override=lambda unit: (130, 130),
        cop_boost=lambda unit: (20, 10),
        scop_boost=lambda unit: (20, 30))

kindle = CommandingOfficer(
        stat_override=lambda unit: (140, 100) if unit.terrain.type.is_urban else (100, 100),
        cop_boost=lambda unit: (50, 10) if unit.terrain.type.is_urban else (10, 10),
        scop_boost=lambda unit: unimplemented("kindle scop not implemented"))

koal = CommandingOfficer(
        stat_override=lambda unit: (110, 100) if unit.terrain == road else (100, 100),
        cop_boost=lambda unit: (20, 10) if unit.terrain == road else (10, 10),
        scop_boost=lambda unit: (30, 10) if unit.terrain == road else (10, 10))

lash = CommandingOfficer(
        stat_override=lambda unit: (100 + 10 * unit.terrain.defense, 100),
        scop_boost=lambda unit: (10 + 10 * unit.terrain.defense, 10 + 10 * unit.terrain.defense))

co_max = CommandingOfficer(
        stat_override=lambda unit: (100, 100) if unit.is_infantry else ((120, 100) if unit.is_direct else (90, 100)),
        cop_boost=lambda unit: (20, 10) if unit.is_direct and not unit.is_infantry else (10, 10),
        scop_boost=lambda unit: (40, 10) if unit.is_direct and not unit.is_infantry else (10, 10))

nell = CommandingOfficer(luck=NELL_LUCK,
        cop_boost=lambda unit: unimplemented("nell cop and scop not implemented"))

rachel_luck = CommandingOfficer(luck=RACHEL_LUCK)

sami = CommandingOfficer(
        stat_override=lambda unit: (130, 100) if unit.is_infantry else ((100, 100) if unit.is_indirect else (90, 100)),
        cop_boost=lambda unit: (30, 10) if unit.is_infantry else (10, 10),
        scop_boost=lambda unit: (50, 10) if unit.is_infantry else (10, 10))

sensei = CommandingOfficer(
        stat_override=lambda unit: (140, 100) if unit.is_infantry else ((150, 100) if unit.is_copter else (
                                   (100, 100) if unit.is_air else (90, 100))),
        cop_boost=lambda unit: (25, 10) if unit.is_copter else (10, 10))

sonja = CommandingOfficer(luck=SONJA_LUCK)

# sonja's counterattacks (when SCOP is not active)
sonja_counter = CommandingOfficer(luck=SONJA_LUCK, stat_override=(lambda unit: 150, 100))

von_bolt = CommandingOfficer(stat_override=lambda unit: (110, 110))
vb = von_bolt


class Unit:

    def __init__(self, unit, co=CommandingOfficer(), power=None, terrain=shoal, raw_hp=Dist([(100, 1)])):
        if isinstance(unit, UnitData):
            self.data = unit
        elif isinstance(unit, UnitType):
            self.data = unit.data
        else:
            raise Exception("Unrecognized unit value: " + repr(unit))
        self.type = self.data.type

        self.co = co
        self.power = power

        if isinstance(terrain, TerrainData):
            self.terrain = terrain
        elif isinstance(terrain, TerrainType):
            self.terrain = terrain.data
        else:
            raise Exception("Unrecognized terrain value: " + repr(terrain))

        self.raw_hp = raw_hp

    def __repr__(self):
        return ("<" + str(self.data.type.name)
                + ", " + str(self.terrain.type.name)
                + ", " + repr(self.raw_hp) + ">")

    is_air = property(lambda self: self.type.is_air)
    is_sea = property(lambda self: self.type.is_sea)
    is_infantry = property(lambda self: self.type.is_infantry)
    is_vehicle = property(lambda self: self.type.is_vehicle)
    is_copter = property(lambda self: self.type.is_copter)
    is_indirect = property(lambda self: self.type.is_indirect)
    is_direct = property(lambda self: self.type.is_direct)

    def with_hp(self, new_hp):
        if isinstance(new_hp, int):
            new_hp = Dist.exactly(new_hp * 10)
        return Unit(self.data, self.co, self.power, self.terrain, new_hp)

    def add_hp(self, addition):
        if isinstance(addition, int):
            addition = Dist.exactly(addition * 10)
        return Unit(self.data, self.co, self.power, self.terrain, self.raw_hp + addition)


    def with_co(self, new_co):
        return Unit(self.data, new_co, self.power, self.terrain, self.raw_hp)

    def with_power(self, new_power):
        return Unit(self.data, self.co, new_power, self.terrain, self.raw_hp)

    def with_terrain(self, new_terrain):
        return Unit(self.data, self.co, self.power, new_terrain, self.raw_hp)
    on = with_terrain

    # allows infantry(4) syntax for hp
    # TODO: allow more short form?
    def __call__(self, *args):
        ret = self
        for arg in args:
            # Allow using the builtin max as an "alias" for the CO, since the function is not a valid argument
            if arg == max:
                arg = co_max

            if isinstance(arg, CommandingOfficer):
                ret = ret.with_co(arg)
            elif isinstance(arg, PowerType):
                ret = ret.with_power(arg)
            elif isinstance(arg, TerrainType) or isinstance(arg, TerrainData):
                ret = ret.with_terrain(arg)
            elif isinstance(arg, Dist) or isinstance(arg, int):
                ret = ret.with_hp(arg)
            else:
                raise Exception("Unrecognized convenience arg:" + repr(arg))
        return ret

    def truncate_hp(self, r):
        if isinstance(r, int):
            r = range((r-1)*10+1, r*10+1)
        return self.with_hp(self.raw_hp.truncate(r))

    @property
    def displayed_hp_raw(self):
        return (self.raw_hp / 10).round_up()

    @property
    def displayed_hp(self):
        return self.displayed_hp_raw.normalize()

    def defense_rating(self, attacker=None):
        co_defense = self.co.defense_for(self, (self.power or DEFENDER_POWER), attacker)
        terrain_defense = self.displayed_hp.scale(self.terrain.defense)
        total_defense = co_defense + terrain_defense
        debug_log("total defense:", total_defense)
        return total_defense

    def base_damage_to(self, other):
        my_index = self.data.type.value - 1
        other_index = other.data.type.value - 1
        return DAMAGE_MATRIX[my_index][other_index]

    def damage_to(self, other):
        debug_log("damage to:", other)

        base_damage = Dist.exactly(self.base_damage_to(other))
        debug_log("base damage:", repr(base_damage))
        co_attack = self.co.attack_for(self, (self.power or ATTACKER_POWER), other)
        debug_log("co attack:", repr(co_attack))

        co_adjusted_damage = (base_damage.scale(co_attack / 100)) + self.co.luck
        hp_adjusted_damage = (self.displayed_hp.clamp(range(10)) / 10) * co_adjusted_damage
        debug_log("adjusted damage", repr(hp_adjusted_damage))

        defense_multiplier = other.defense_rating(self).transform(lambda v: (200 - v) / 100)
        debug_log("defense multiplier:", repr(defense_multiplier))

        raw_damage = hp_adjusted_damage * defense_multiplier
        debug_log("raw damage:", repr(raw_damage))
        final_damage = raw_damage.round_awars()
        debug_log("final damage:", repr(final_damage))

        return final_damage

    def attack_with(self, *args):
        if not args:
            return self
        other, *remaining = args

        total_new_raw_hp = Dist([])
        for displayed_hp, chance in self.displayed_hp.normalize()._buckets:
            partial_self = self.truncate_hp(displayed_hp)
            damage = other.damage_to(partial_self)
            new_raw_hp = partial_self.raw_hp - damage
            debug_log("displayed hp", displayed_hp, "has new raw hp:", repr(new_raw_hp))
            total_new_raw_hp = total_new_raw_hp.vector_add(new_raw_hp)
            debug_log("total raw hp is now:", repr(total_new_raw_hp))
            debug_log()

        return self.with_hp(total_new_raw_hp).attack_with(*remaining)
    attack_With = attack_with


def pretty_print(units):
    for unit in units:
        print(unit.with_hp(unit.displayed_hp.clamp(range(10))))

def battle(attacker, defender, rounds=1):
    for r in range(rounds):
        if r % 2 == 1:
            attacker, defender = defender, attacker

        # TODO: handle bonus counter damage
        defender_after = defender.attack_with(attacker)
        attacker_after = attacker.attack_with(defender_after)

        attacker, defender = attacker_after, defender_after

        if r % 2 == 1:
            attacker, defender = defender, attacker
    return attacker, defender

def print_table(rows):
    row_format = "{:>10}" * (len(rows[0]))
    row_format = "".join("{:>" + str(max(len(cell) for cell in col) + 1) + "}" for col in zip(*rows))
    for row in rows:
        print(row_format.format(*row))


def compare_damage(*attackers, defenders=None, prune=True):
    if defenders is None:
        defenders = ALL_UNITS
    if prune:
        defenders = [d for d in defenders if all(a.damage_to(d)[0] > 0 for a in attackers)]
    header = [""] + [attacker.type.name for attacker in attackers]
    rows = [header]
    for unit in defenders:
        row = [unit.type.name] + [str(attacker.damage_to(unit)[0]) for attacker in attackers]
        rows.append(row)
    print_table(rows)
    # print("\n".join("\t".join(col for col in row) for row in rows))


ALL_UNITS = [Unit(ut) for ut in UnitType]

# Convenience Variables
anti_air = Unit(UnitType.anti_air)
aa = anti_air
apc = Unit(UnitType.apc)
artillery = Unit(UnitType.artillery)
arti = artillery
bcopter = Unit(UnitType.bcopter)
bopter = bcopter
battleship = Unit(UnitType.battleship)
black_boat = Unit(UnitType.black_boat)
black_bomb = Unit(UnitType.black_bomb)
bomber = Unit(UnitType.bomber)
carrier = Unit(UnitType.carrier)
cruiser = Unit(UnitType.cruiser)
fighter = Unit(UnitType.fighter)
infantry = Unit(UnitType.infantry)
inf = infantry
lander = Unit(UnitType.lander)
md_tank = Unit(UnitType.md_tank)
md = md_tank
mech = Unit(UnitType.mech)
mega_tank = Unit(UnitType.mega_tank)
mega = mega_tank
missile = Unit(UnitType.missile)
neotank = Unit(UnitType.neotank)
neo = neotank
piperunner = Unit(UnitType.piperunner)
recon = Unit(UnitType.recon)
rocket = Unit(UnitType.rocket)
stealth = Unit(UnitType.stealth)
sub = Unit(UnitType.sub)
tcopter = Unit(UnitType.tcopter)
tank = Unit(UnitType.tank)

