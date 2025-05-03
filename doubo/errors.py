class DouboError(Exception):
    """Base exception for all doubo errors."""
    pass


class ConnectionError(DouboError):
    """Raised when there is an error connecting to MetaTrader 5."""
    pass


class DataError(DouboError):
    """Raised when there is an error with data processing."""
    pass
