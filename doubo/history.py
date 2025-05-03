import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import MetaTrader5 as mt5

from doubo.constants import (
    DEAL_ENTRY_NAMES,
    DEAL_REASON_NAMES,
    DEAL_TYPE_NAMES,
)
from doubo.errors import DataError


def get_deal_history(
    start_date: datetime,
    end_date: datetime,
) -> List[Dict[str, Any]]:
    """Retrieve deal history from MetaTrader 5 between the specified dates.
    
    Args:
        start_date: Start date for history retrieval (inclusive)
        end_date: End date for history retrieval (exclusive)
        
    Returns:
        List of deals as dictionaries with additional name fields
        
    Raises:
        HistoryError: If history deals cannot be retrieved
    """
    start_ts = get_timestamp(start_date)
    end_ts = get_timestamp(end_date)
    deals = mt5.history_deals_get(start_ts, end_ts)
    if deals is None:
        raise DataError("Failed to get history deals.")

    deals_parsed = [deal._asdict() for deal in deals]
    for deal in deals_parsed:
        deal['type_name'] = DEAL_TYPE_NAMES.get(deal['type'], "Unknown")
        deal['entry_name'] = DEAL_ENTRY_NAMES.get(deal['entry'], "Unknown")
        deal['reason_name'] = DEAL_REASON_NAMES.get(deal['reason'], "Unknown")
    return deals_parsed


def save_deals_to_csv(
    deals: List[Dict[str, Any]], 
    save_dir: Path, 
    filename: str
) -> Path:
    """Save deal history to a CSV file and return the file path.
    
    Args:
        deals: List of deals to save
        save_dir: Directory to save the CSV file
        filename: Name of the CSV file
        
    Returns:
        Path to the saved CSV file
    """
    save_dir_path = save_dir / str(round(time.time()))
    save_dir_path.mkdir(parents=True, exist_ok=True)
    
    keys = deals[0].keys()
    csv_file_path = save_dir_path / filename
    with open(csv_file_path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, keys)
        writer.writeheader()
        writer.writerows(deals)
    
    return csv_file_path


def get_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp."""
    return round((dt - datetime(1970, 1, 1)).total_seconds())
