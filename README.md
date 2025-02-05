# doubo
Place a buy and a sell order in one go on MetaTrader5.

## Pre-requisite

`doubo` interacts with MetaTrader5 to place orders.
It is required to have MetaTrader5 installed before using `doubo`.

## Installation

`doubo` can be installed using `pip`:

```shell
pip install doubo
```

Note that `doubo` depends on MetaTrader's official Python library, which is only available on Windows x86 platform.

## Usage

As of v1.0, only real time market orders are supported:

```shell
doubo place <SYMBOL> <VOLUME> <STOP_LOSS_PIPS> <TAKE_PROFIT_PIPS>
```

An example command to place 0.01 double-end orders on EUR/USD forex with 50 pips stop loss and doubled take profit:

```shell
doubo place EURUSD 0.01 50 100
```

## License

[MIT license](LICENSE)
