# doubo
Place a buy and a sell order in one go on MetaTrader5.

## Disclaimer

This tool is provided for informational purposes only and does not constitute financial advice. Users should consult with a qualified financial advisor before making any trading decisions. Additionally, opening two positions in opposite directions simultaneously may violate regulations or policies of certain brokers. Use this tool at your own risk.

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
doubo place <SYMBOL> <VOLUME> [--sl <STOP_LOSS_PIPS> | --tp <TAKE_PROFIT_PIPS>]
```

An example command to place 0.01 double-end orders on EUR/USD forex with 50 pips stop loss and doubled take profit:

```shell
doubo place EURUSD 0.01 --sl 50 --tp 100
```

## License

[MIT license](LICENSE)
