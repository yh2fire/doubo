import re
import time
from datetime import datetime, timedelta
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
    
    buy_price = round(symbol_info.ask, symbol_info.digits)
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
        "comment": f"doubo@{buy_price}", # request max length is 32 (?) while MetaTrader5 display limit is 16
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

    sell_price = round(symbol_info.bid, symbol_info.digits)
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
        "comment": f"doubo@{sell_price}", # request max length is 32 (?) while MetaTrader5 display limit is 16
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


@app.command()
@app.command("g", hidden=True)
def gappy(
    symbol: Annotated[str, typer.Argument(
        help="The symbol to place the buy and sell orders on.",
    )],
    volume: Annotated[float, typer.Argument(
        help="The volume of the buy and sell orders.",
    )],
    market_open_at: Annotated[str, typer.Option(
        "--market-open-at",
        "-O",
        help=(
            "The market open time in the format of 'HH:MM', "
            "ex: '09:00'. "
            "Default is '00:00'."
        ),
    )] = "00:00",
    open_after: Annotated[str, typer.Option(
        "--open-after",
        "-o",
        help=(
            "The time to open the position after the market open time "
            "in the format of '<number>[s|m|h]', "
            "ex: '1m15s' for 1 minute and 15 seconds. "
            "Default is '10s', that is say, 10 seconds."
        ),
    )] = "10s",
    close_after: Annotated[str, typer.Option(
        "--close-after",
        "-c",
        help=(
            "The time to close the position after the position open time "
            "in the format of '<number>[s|m|h]', "
            "ex: '3h40m' for 3 hours and 40 minutes. "
            "Default is '1h', that is say, 1 hour."
        ),
    )] = "1h",
    fill_gap_ratio: Annotated[float, typer.Option(
        "--fill-gap-ratio",
        "-f",
        help=(
            "The ratio of the gap to fill as target "
            "in the range of [0, 1]. "
            "Default is 1.0."
        ),
    )] = 1.0,
    min_gap_pips: Annotated[int, typer.Option(
        "--min-gap-pips",
        "-m",
        help="The minimum gap in pips to open the position. Default is 100.",
    )] = 100,
    max_gap_pips: Annotated[int, typer.Option(
        "--max-gap-pips",
        "-M",
        help="The maximum gap in pips to open the position. Default is 10000.",
    )] = 10000,
):
    try:
        market_open_time = datetime.strptime(market_open_at, "%H:%M").time()
    except ValueError:
        fail(f"Invalid market open time format: {market_open_at}. Expected 'HH:MM'.")

    try:
        open_after_seconds = parse_time_delta(open_after)
    except ValueError:
        fail(f"Invalid open time format: {open_after}. Expected '<number>[s|m|h]'.")

    try:
        close_after_seconds = parse_time_delta(close_after)
    except ValueError:
        fail(f"Invalid close time format: {close_after}. Expected '<number>[s|m|h]'.")

    if not (0 < fill_gap_ratio <= 1):
        fail(f"fill_gap_ratio must be between (0, 1], got {fill_gap_ratio}.")

    execute_gappy(
        symbol,
        volume,
        market_open_time,
        open_after_seconds,
        close_after_seconds,
        fill_gap_ratio,
        min_gap_pips,
        max_gap_pips,
    )


def parse_time_delta(time_str: str) -> int:
    """Parse a time string like '1h30m15s' into seconds."""
    pattern = re.compile(r'((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?')
    match = pattern.fullmatch(time_str)
    if not match:
        raise ValueError(f"Invalid time format: {time_str}")
    time_params = {k: int(v) for k, v in match.groupdict(default=0).items()}
    return int(timedelta(**time_params).total_seconds())


def fail(message: str):
    """Print an error message in red and abort the program."""
    print(f"[red]{message}[/red]")
    raise typer.Abort()


def execute_gappy(
    symbol: str,
    volume: float,
    market_open_time: datetime.time,
    open_after_seconds: int,
    close_after_seconds: int,
    fill_gap_ratio: float,
    min_gap_pips: int,
    max_gap_pips: int,
):
    """Execute the gappy trading logic assuming all parameters are valid."""
    # Initialize MetaTrader5 and select symbol
    if not mt5.initialize():
        fail("Failed to initialize MetaTrader5 connection.")
    if not mt5.symbol_select(symbol, True):
        fail(f"Failed to select symbol {symbol}.")

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        fail(f"Failed to get symbol info for {symbol}.")

    # Ensure the market is closed
    # TODO: should input market open day instead of assuming today
    market_status = mt5.market_book_add(symbol)
    if market_status:
        fail(
            "Gappy is designed to be scheduled when the market is closed. "
            "Market is currently open. Please try again later."
        )

    # Get last close price
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
    if not rates:
        fail("Failed to fetch market data.")
    last_close_price = rates[0]['close']
    print(f"Last close price: {last_close_price}")

    # Determine market open datetime (today or tomorrow)
    now = datetime.now()
    market_open_datetime = datetime.combine(now.date(), market_open_time)
    if market_open_datetime <= now:
        market_open_datetime += timedelta(days=1)

    print(
        f"Waiting for market open at {market_open_datetime} "
        f"and order open after {open_after_seconds} seconds. "
        "Please keep the [bold red]terminal[/bold red] and "
        "[bold red]MetaTrader5[/bold red] open."
    )

    # Wait until market open time plus open_after
    target_open_time = market_open_datetime + timedelta(seconds=open_after_seconds)
    while datetime.now() < target_open_time:
        time.sleep(1)

    # Get current tick data
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        fail(f"Failed to get tick data for {symbol}.")

    # Determine order type and calculate gap
    if tick.bid > last_close_price:  # Sell
        gap = tick.bid - last_close_price
        order_type = mt5.ORDER_TYPE_SELL
        current_price = tick.bid
        target_price = current_price - gap * fill_gap_ratio
    else:  # Buy
        gap = last_close_price - tick.ask
        order_type = mt5.ORDER_TYPE_BUY
        current_price = tick.ask
        target_price = current_price + gap * fill_gap_ratio

    gap_pips = round(gap / symbol_info.point)

    print(f"Gap = {gap_pips} pips, price = {current_price}, target = {target_price}.")

    # Check if the gap is within the range
    if gap_pips < min_gap_pips or gap_pips > max_gap_pips:
        fail(f"Gap of {gap_pips} pips is out of range [{min_gap_pips}, {max_gap_pips}].")

    # Place order
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": current_price,
        "tp": target_price,
        "deviation": 10,
        "magic": MAGIC,
        "comment": f"gappy@{current_price}",
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        fail(f"Failed to place order: {result.comment}")
    ticket_id = result.order

    order_type_str = "SELL" if order_type == mt5.ORDER_TYPE_SELL else "BUY"
    print(
        f"{symbol} {order_type_str} {volume} @ {current_price}, "
        f"tp = {target_price} (ticket {ticket_id})."
    )

    print(
        f"Waiting for {close_after_seconds} seconds to close the position."
        " Please keep the [bold red]terminal[/bold red] and "
        "[bold red]MetaTrader5[/bold red] open."
    )

    # Wait until close_after time
    close_time = datetime.now() + timedelta(seconds=close_after_seconds)
    while datetime.now() < close_time:
        time.sleep(1)

    # Close the position
    # TODO: closing logic is not solid, tick price may change sharply, if closing fails, should re-fetch tick price then retry closing
    tick = mt5.symbol_info_tick(symbol)
    while tick is None:
        fail(f"Failed to get tick data for {symbol}.")
        time.sleep(1)
        tick = mt5.symbol_info_tick(symbol)
    close_price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask
    close_type = (
        mt5.ORDER_TYPE_BUY
        if order_type == mt5.ORDER_TYPE_SELL
        else mt5.ORDER_TYPE_SELL
    )
    close_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": close_type,
        "price": close_price,
        "deviation": 10,
        "magic": MAGIC,
        "position": ticket_id,
    }
    close_result = mt5.order_send(close_request)
    while close_result.retcode != mt5.TRADE_RETCODE_DONE:
        fail(f"Failed to close position: {close_result.comment}")
        time.sleep(1)
        close_result = mt5.order_send(close_request)

    profit = mt5.order_calc_profit(
        order_type,
        symbol,
        volume,
        current_price,
        close_price,
    )
    print(f"Position closed, profit: {profit}")


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
