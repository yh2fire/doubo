from typing_extensions import Annotated

import MetaTrader5 as mt5
import typer
from rich import print

from doubo.__about__ import __version__


app = typer.Typer(name="doubo", no_args_is_help=True)


MAGIC = 309613


@app.command()
@app.command("p", hidden=True)
def place(
    symbol: Annotated[str, typer.Argument(
        help="The symbol to place the buy and sell orders on.",
    )],
    volume: Annotated[float, typer.Argument(
        help="The volume of the buy and sell orders.",
    )],
    sl: Annotated[int, typer.Option(
        "--sl",
        "-s",
        help="The stop loss in pips.",
    )] = 50,
    tp: Annotated[int, typer.Option(
        "--tp",
        "-t",
        help="The take profit in pips.",
    )] = 100,
    deviation: Annotated[int, typer.Option(
        "--deviation",
        "-d",
        help="The maximum deviation in points.",
    )] = 10,
):
    print(
        f"Placing buy and sell orders on {symbol} with volume {volume}, "
        f"stop loss {sl} pips and take profit {tp} pips."
    )

    if not mt5.initialize():
        raise RuntimeError(
            f"Failed to initialize MetaTrader5 connection, "
            f"code = {mt5.last_error()}."
        )
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(
            f"Failed to select symbol {symbol}, "
            f"code = {mt5.last_error()}."
        )
    
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise RuntimeError(
            f"Failed to get symbol info for {symbol}, "
            f"code = {mt5.last_error()}."
        )
    
    buy_price = symbol_info.ask
    buy_sl = round(buy_price - sl * symbol_info.point, symbol_info.digits)
    buy_tp = round(buy_price + tp * symbol_info.point, symbol_info.digits)
    buy_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": buy_price,
        "sl": buy_sl,
        "tp": buy_tp,
        "deviation": deviation,
        "magic": MAGIC,
        "comment": f"doubo buy at {buy_price}",
    }
    print(f"Sending buy order at {buy_price} with SL {buy_sl} & TP {buy_tp}.")
    buy_result = mt5.order_send(buy_request)
    if buy_result is None:
        raise RuntimeError(
            f"Failed to send buy order, code = {mt5.last_error()}."
        )
    if buy_result.retcode != mt5.TRADE_RETCODE_DONE:
        print(buy_result._asdict())
        raise RuntimeError(
            f"Failed to send buy order, error = {buy_result.comment}."
        )
    print(f"Buy order placed with ticket {buy_result.order}")

    sell_price = symbol_info.bid
    sell_sl = round(sell_price + sl * symbol_info.point, symbol_info.digits)
    sell_tp = round(sell_price - tp * symbol_info.point, symbol_info.digits)
    sell_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": sell_price,
        "sl": sell_sl,
        "tp": sell_tp,
        "deviation": deviation,
        "magic": MAGIC,
        "comment": f"doubo sell at {sell_price}",
    }
    print(f"Sending sell order at {sell_price} with SL {sell_sl} & TP {sell_tp}.")
    sell_result = mt5.order_send(sell_request)
    if sell_result is None:
        raise RuntimeError(
            f"Failed to send sell order, code = {mt5.last_error()}."
        )
    if sell_result.retcode != mt5.TRADE_RETCODE_DONE:
        print(sell_result._asdict())
        raise RuntimeError(
            f"Failed to send sell order, error = {sell_result.comment}."
        )
    print(f"Sell order placed with ticket {sell_result.order}.")

    print("Done.")


def version_callback(value: bool):
    if value:
        print(f"[green]{__version__}")
        raise typer.Exit()


@app.callback()
def common(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        is_eager=True,
        callback=version_callback,
    ),
):
    pass
