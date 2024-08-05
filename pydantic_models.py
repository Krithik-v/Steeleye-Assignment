from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Trade(BaseModel):
    asset_class: str
    counterparty: str
    instrument_id: str
    instrument_name: str
    trade_date_time: str
    buySellIndicator: str
    price: int
    quantity: int
    trade_id: str
    trader: str


#
#
class Trades(BaseModel):
    data: List[Trade]
