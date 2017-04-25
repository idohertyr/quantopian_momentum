# quantopian_momentum


### Author: Ian Doherty
### Date: April 13, 2017

These algorithms trade using Momentum stategies.

### RVI.py (Relative Vigor Index)
#### INPUTS: OHLC prices

```
a = close - open <br />
b = close - open // one bar prior to a
c = close - open // one bar prior to b
d = close - open // one bar prior to c
numerator = ( a + (2 * b) + (2 * c) + d ) / 6
```
```
e = high - low // of bar a
f = high - low // of bar b
g = high - low // of bar c
h = high - low // of bar d
denominator = ( e + (2 * f) + (2 * g) + h) / 6
```

```
Current period selected = 20

RVI = SMA of numerator for selected period /
        SMA of denominator for selected period
```

#### SIGNAL_LINE
```
i = RVI // one bar prior
j = RVI // one bar prior to i
k = RVI // one bar prior to j
SIGNAL_LINE = (RVI + (2 * i) + (2 * j) + k) / 6
```
