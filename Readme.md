# Discrete Probability Calculator

This repository has two parts:
1. A game-agnostic library for calculating discrete probability distributions (`dist.py`). 
2. An "n-hit-ko" damage calculator for advance wars built using that library (`awars.py`).

## dist.py

I wrote dist.py as a tool to help me calculate probability distributions for dice rolls in Dungeons & Dragons 5th Edition.

The core concept of the library is a `Dist` class that represents a discrete probability distribution. Concretely, each `Dist` is a set of weighted buckets, like a dictionary where each key is a possible outcome and each value is the relative likelihood of that outcome. You can then manipulate and combine the `Dist` objects to calculate the probability for specific dice rolls.

You can use the library in a python repl like so:

```
$ python -i dist.py 
>>> d6
Dist([(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1)])
>>> d6 + 1
Dist([(2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)])
```

You can combine probability distributions by adding them:
```
>>> d6 + d6
Dist([(2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 5), (9, 4), (10, 3), (11, 2), (12, 1)])
>>> 2 * d6
Dist([(2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 5), (9, 4), (10, 3), (11, 2), (12, 1)])
```

You can visualize distributions and print other statistical details about them:
```
>>> print((2 * d6 + 3).normalize().details())
5:  (0.03) ###                 
6:  (0.06) ######              
7:  (0.08) ##########          
8:  (0.11) #############       
9:  (0.14) ################    
10: (0.17) ####################
11: (0.14) ################    
12: (0.11) #############       
13: (0.08) ##########          
14: (0.06) ######              
15: (0.03) ###                 
each # represents 0.01
mean: 10.00, stdev: 2.42, median: 10.00
within 1 stdev (68%): 7.58 - 12.42
within 2 stdev (95%): 5.17 - 14.83
```

You can check the likelihood that an ability check meets a certain threshold:
```
>>> d20 + 5
Dist([(6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1), (19, 1), (20, 1), (21, 1), (22, 1), (23, 1), (24, 1), (25, 1)])
>>> (d20 + 5).pass_fail(17).normalize()
Dist([(0, 0.55), (1, 0.45)])
>>> (d20 + 5).advantage().pass_fail(17).normalize()
Dist([(0, 0.3025), (1, 0.6975)])
```

And you can compute expected value for attacks by multiplying the to-hit distribution by the damage distribution:

```
>>> to_hit = (d20 + 5).pass_fail(14) # chance of hitting an AC of 14 with a +5 attack bonus
>>> damage = 2 * d6 + 3              # 2d6 + 3 damage
>>> print((to_hit * damage).normalize().details())
0:  (0.40) ####################
5:  (0.02)                     
6:  (0.03) #                   
7:  (0.05) ##                  
8:  (0.07) ###                 
9:  (0.08) ####                
10: (0.10) #####               
11: (0.08) ####                
12: (0.07) ###                 
13: (0.05) ##                  
14: (0.03) #                   
15: (0.02)                     
each # represents 0.02
mean: 6.00, stdev: 5.24, median: 7.50
within 1 stdev (68%): 0.76 - 11.24
within 2 stdev (95%): -4.49 - 16.49
```

## awars.py

The advance wars damage calculator can be similarly run in the python repl. The syntax is built around unit objects with certain manipulatable properties (terrain, CO, whether a power is active) and a distribution of health. The main "verb" is the `attack_with()` method which simulates attacking the given unit with one or more other units. It evaluates to a new unit object with a distribution of HP.

```
$ python -i awars.py
11NN>>> tank
<tank, shoal, Dist([(100, 1)])>
11NN>>> tank(city)
<tank, city, Dist([(100, 1)])>
11NN>>> tank(city).attack_with(tank)
<tank, city, Dist([(52, 1.0), (53, 2.0), (54, 1.0), (55, 2.0), (56, 1.0), (57, 2.0), (58, 1.0)])>
```

You can simulate an attack with multiple units by passing multiple units to the attack_with function. You can convert the "true hp" to displayed hp using the displayed_hp property. This is useful for calculating the likelihood of a 2hko, 3hko, or more :)
```
11NN>>> tank(city).attack_with(tank, tank)
<tank, city, Dist([(-5, 1.0), (-4, 3.0), (-3, 4.0), (-2, 6.0), (-1, 7.0), (0, 10.0), (1, 12.0), (2, 11.0), (3, 12.0), (4, 10.0), (5, 9.0), (6, 7.0), (7, 4.0), (8, 3.0), (9, 1.0)])>
11NN>>> tank(city).attack_with(tank, tank).displayed_hp
Dist([(0, 0.31), (1, 0.69)])
11NN>>> tank(city).attack_with(tank, tank, inf).displayed_hp
Dist([(-1, 0.318), (0, 0.654), (1, 0.028)])
11NN>>> tank(city).attack_with(tank, tank, aa).displayed_hp
Dist([(-4, 0.005), (-3, 0.424), (-2, 0.558), (-1, 0.013)])
```

The calculator assumes 1 tower by default, but you can set different numbers of towers using `set_meta()`:
```
11NN>>> get_meta()
{'towers': 1, 'dtowers': 1, 'attacker_power': <PowerType.no_power: 1>, 'defender_power': <PowerType.no_power: 1>}
11NN>>> set_meta(2) # set number of towers to 2
22NN>>> get_meta()
{'towers': 2, 'dtowers': 2, 'attacker_power': <PowerType.no_power: 1>, 'defender_power': <PowerType.no_power: 1>}
```

This shows that 120 attack tanks are guaranteed to 2hko a vanilla tank on city:
```
22NN>>> tank(city).attack_with(tank, tank).displayed_hp
Dist([(-1, 0.26), (0, 0.74)])
```

Because the result of `attack_with()` is just another unit object, you can manipulate that unit object to simulate it changing over time, e.g. by moving onto a different terrain tile. This shows how much more likely you are to kill a tank with a second tank shot if it moved from city to plains in between:
```
11NN>>> tank(city).attack_with(tank)
<tank, city, Dist([(52, 1.0), (53, 2.0), (54, 1.0), (55, 2.0), (56, 1.0), (57, 2.0), (58, 1.0)])>
11NN>>> tank(city).attack_with(tank).with_terrain(plains)
<tank, plains, Dist([(52, 1.0), (53, 2.0), (54, 1.0), (55, 2.0), (56, 1.0), (57, 2.0), (58, 1.0)])>
11NN>>> tank(city).attack_with(tank).with_terrain(plains).attack_with(tank).displayed_hp
Dist([(-1, 0.14), (0, 0.82), (1, 0.04)])
```

Here's another concrete example showing how you can track chip damage from a tank that took infantry counterattack damage before sitting on a city. Notice how it's much more likely to get 2hko'd than a tank with no chip!

```
11NN>>> tank(plains).attack_with(inf(5))
<tank, plains, Dist([(94, 2.0), (95, 2.0), (96, 2.0), (97, 2.0), (98, 2.0)])>
11NN>>> tank(plains).attack_with(inf(5)).with_terrain(city).attack_with(tank, tank).displayed_hp
Dist([(-1, 0.054), (0, 0.706), (1, 0.24)])
```
