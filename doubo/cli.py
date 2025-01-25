from typing_extensions import Annotated

import typer
from rich import print

from doubo.__about__ import __version__


app = typer.Typer(name="doubo", no_args_is_help=True)


@app.command()
@app.command("p", hidden=True)
def place(
    symbol: Annotated[str, typer.Argument(
        ...,
        help="The symbol to place the buy and sell orders on.",
    )],
    volume: Annotated[float, typer.Argument(
        ...,
        help="The volume of the buy and sell orders.",
    )],
    sl: Annotated[float, typer.Argument(
        ...,
        help="The stop loss price.",
    )],
    tp: Annotated[float, typer.Argument(
        ...,
        help="The take profit price.",
    )],
):
    print(f"Placing buy and sell orders on {symbol} with volume {volume}.")
    print(f"Stop loss price: {sl}.")
    print(f"Take profit price: {tp}.")
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
