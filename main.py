from math import ceil
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from typing import Optional
import json
from pathlib import Path
from pydantic_models import Trade, Trades
from typing import List

app = FastAPI()
TRADES_DATA_FILE = Path("trades_data.json")


async def load_trades_data() -> List[Trade]:
    """
    Loads the mock JSON data and returns it.

    :return: Static List of Dicts
    """
    return Trades(**dict(data=json.loads(TRADES_DATA_FILE.read_text()))).data


def sort_trade_by_price(trade, desc):
    sort_by_price = lambda x: x.price.price
    return sorted(trade, key=sort_by_price, reverse=desc)


def sort_trade_by_quantity(trade, desc):
    sort_by_quantity = lambda x: x.trade_quantity.quantity
    return sorted(trade, key=sort_by_quantity, reverse=desc)


def sort_trade_by_date(trade, desc):
    sort_by_date = lambda x: x.order_submit
    return sorted(trade, key=sort_by_date, reverse=desc)


def sortResults(trade, sort_by, desc):
    if sort_by == "Price":
        return sort_trade_by_price(trade, desc)
    elif sort_by == "Quantity":
        return sort_trade_by_quantity()
    elif sort_by == "date":
        return sort_trade_by_date(trade, desc)
    else:
        return "Invalid input"


@app.get("/trade/{trade_id}")
async def get_trade(trade_id: str, trades: List[Trade] = Depends(load_trades_data)):
    """
    Can fetch the single trade from its Trade ID.
    """
    result = []
    for trade in trades:
        if trade.trade_id == trade_id:
            result = {"status": "success", "trade": trade}
            break
    if not result:
        raise HTTPException(status_code=404, detail=f"Trade id: {trade_id} not found!")

    return result


# listing
@app.get("/listing")
async def read_trades(
    page: int,
    trades: List[Trades] = Depends(load_trades_data),
    page_rate: Optional[int] = 10,
    sort_by: Optional[str] = None,
    is_desc: Optional[bool] = False,
):
    """
    Can retrive all the of Trades from list.
    """

    page = page - 1
    result_trades = trades
    number_of_trades = len(result_trades)

    if number_of_trades == 0:
        raise HTTPException(status_code=404, detail="No trades found!")
    if page_rate < 0:
        raise HTTPException(status_code=400, detail="Oops! Invalid page rate")
    number_of_pages = ceil(number_of_trades / page_rate)
    if page >= number_of_pages or page < 0:
        raise HTTPException(status_code=404, detail="Oops! Page not found")
    if sort_by:
        result_trades = sortResults(result_trades, sort_by, is_desc)
        if isinstance(result_trades, str):
            return {
                "sortbyReceived": sort_by,
                "sortbyList": Trades,
            }
            raise HTTPException(
                status_code=404, detail="Oops! Invalid sortby property name"
            )

    result = {
        "page": str(page + 1) + "/" + str(number_of_pages),
        "page_rate": page_rate,
        "total_trades": number_of_trades,
        "results": result_trades[page * page_rate : (page + 1) * page_rate],
    }
    return result


#
@app.get("/search-trade")
async def search_trade(
    page: int,
    search: str,
    trades: List[Trade] = Depends(load_trades_data),
    page_rate: Optional[int] = 10,
    case_sensitive: Optional[bool] = False,
    sort_by: Optional[str] = None,
    is_desc: Optional[bool] = False,
):
    """
    Can search the Trade from the particular attributes.
    """
    page = page - 1
    if page_rate <= 0:
        return {"status": "failure", "message": "Oops! Invalid page rate"}, 400
    search = search if case_sensitive else search.lower()
    search_Results = []
    for trade in trades:
        instrument_id = (
            trade.instrument_id.lower() if not case_sensitive else trade.instrument_id
        )
        instrument_name = (
            trade.instrument_name.lower()
            if not case_sensitive
            else trade.instrument_name
        )
        counterparty = (
            trade.counterparty.lower() if not case_sensitive else trade.counterparty
        )
        if (
            search in instrument_id
            or search in instrument_name
            or search in counterparty
        ):
            search_Results.append(trade)

    number_of_trades = len(search_Results)
    if number_of_trades == 0:
        raise HTTPException(status_code=404, detail="No trades found")

    number_of_pages = ceil(number_of_trades / page_rate)
    if page >= number_of_pages or page < 0:
        raise HTTPException(status_code=404, detail="Page not found")

    if sort_by:
        search_Results = sortResults(search_Results, sort_by, is_desc)
        if isinstance(search_Results, str):
            return {
                "status": "failure",
                "message": "Invalid sortby property name",
                "sortbyReceived": sort_by,
                "sortbyList": Trade,
            }, 400

    result = {
        "status": "success",
        "page": str(page + 1) + "/" + str(number_of_pages),
        "page_rate": page_rate,
        "total_trades": number_of_trades,
        "trades": search_Results[page * page_rate : (page + 1) * page_rate],
    }

    return result


#
@app.get("/filter-trades")
async def filter_trades(
    page: int,
    trades: List[Trade] = Depends(load_trades_data),
    page_rate: Optional[int] = 10,
    asset_class: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[int] = None,
    trade_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    is_desc: Optional[bool] = False,
):
    """
    Returns the filtered trades based on the values provided.
    """
    page = page - 1
    if page_rate <= 0:
        raise HTTPException(status_code=400, detail="Oops! Invalid page rate")
    filteredTrades = trades

    if asset_class:
        filteredTrades = [
            trade for trade in filteredTrades if trade.asset_class == asset_class
        ]

    if max_price:
        filteredTrades = [trade for trade in filteredTrades if trade.price <= max_price]
    if min_price:
        filteredTrades = [trade for trade in filteredTrades if trade.price >= min_price]

    if trade_type:

        filteredTrades = [
            trade for trade in filteredTrades if trade.buySellIndicator == trade_type
        ]

    number_of_trades = len(filteredTrades)
    if number_of_trades == 0:
        raise HTTPException(status_code=404, detail="No trades found")
    number_of_pages = ceil(number_of_trades / page_rate)

    if page >= number_of_pages or page < 0:
        raise HTTPException(status_code=404, detail="Page not found")

    if sort_by:
        filteredTrades = sortResults(filteredTrades, sort_by, is_desc)
        if isinstance(filteredTrades, str):
            return {
                "sortbyReceived": sort_by,
                "sortbyList": Trade,
            }
            raise HTTPException(status_code=400, detail="Invalid sortby property name")

    result = {
        "page": str(page + 1) + "/" + str(number_of_pages),
        "page_rate": page_rate,
        "total_trades": number_of_trades,
        "trades": filteredTrades[page * page_rate : (page + 1) * page_rate],
    }
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", port=5556)
