quantopian_momentum
----

#### Author: Ian Doherty
#### Date: April 13, 2017

This algorithm holds indicators for trading momentum, it does not contain a strategy!

### RVI (Relative Vigor Index - Oscillator indicator)

##### INPUTS: OHLC prices

##### Numerator
```python
a = close - open <br />
b = close - open // one bar prior to a
c = close - open // one bar prior to b
d = close - open // one bar prior to c
numerator = ( a + (2 * b) + (2 * c) + d ) / 6
```
##### Denominator
```python
e = high - low // of bar a
f = high - low // of bar b
g = high - low // of bar c
h = high - low // of bar d
denominator = ( e + (2 * f) + (2 * g) + h) / 6
```
##### RVI given select period
```python
Current period selected = 20

RVI = SMA of numerator for selected period /
        SMA of denominator for selected period
```
##### Signal Line
```python
i = RVI // one bar prior
j = RVI // one bar prior to i
k = RVI // one bar prior to j
SIGNAL_LINE = (RVI + (2 * i) + (2 * j) + k) / 6
```

### RSI (Relative Strength Index - Momentum indicator)
```python
RSI = 100-100/(1+RS)
RS = Average gain of up periods w specifed period/
    Average loss of down periods during a specified period
```
##### The RSI in this algorithm is calculated using talib

### Bollinger bands ( - Volatility indicator)
```python
    1. Moving average
    2. Upper band at K times an N-period standard deviation
    3. Lower band at K times an N-period standard deviation
```

##### This Bollinger Bands in this algorithm is calculated with talib

### CCI (Commodity channel index - Oscillator indicator)
```python
CCI = Price - MA / 0.015 x D
```

##### The CCI in this algorithm is calculated with talib