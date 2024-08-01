from math import ceil
import uvicorn
from fastapi import FastAPI
import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field
import random
from random import randrange, randint

app = FastAPI()


class Results(BaseModel):
    asset_class: str = Field(alias="assestClass", description="Asset class of the order. Ex:-Equity,Bond,etc..")
    counterparty: str = Field(alias="countpartyName", description="Counterparty of the order who assited")
    data_source_name: str = Field(alias="dataSourceName",
                                  description="The name of the data source through which order the was placed")
    instrument_id: str = Field(alias="instrumentId",
                               description="The ID of the data source which was ordered. Ex:- GOOG,APL,IBM")
    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument ordered.")
    order_submit: dt.datetime = Field(alias="orderSubmitted", description="The date-time the order was submitted")
    purchase_type: str = Field(alias="purchaseType", description="A value of BUY for buys, SELL for sells")
    order_price: float = Field(alias="tradePrice", description="The price of the Trade.")
    trade_quantity: int = Field(alias="tradeQuantity", description="The amount of units ordred")
    order_Id: str = Field(alias="orderID", description="Id of the trade done.")


##Constants

asset_classes = ["Bond", "Equity", "Crypto", "Stock"]
first_names = ["Irvin", "Lindsay", "Selina", "Alanna", "Desmond", "Gabriela", "Pearl", "Stetson", "Jazlynn", "Kyara",
               "Darrin", "Kylan", "Kameron", "Laney", "Kelis"]
last_names = ["Richard", "Funk", "Blanchard", "Orellana", "Mull", "Willingham", "Earley", "Schell", "Sheehan", "Galvez",
              "Tuck", "Kinder", "Sadler", "Oreilly", "Levy"]
data_source_names = ["Steeleye", "Upstox", "Groww", "Zerodha", "Angelone"]
instrument_names = {"FLPK": "Flipkart", "AMAZ": "Amazon", "TT": "TATA", "NFX": "Netflix", "NVDA": "Nvidia",
                    "APL": "Apple", "GOOG": "Google", "MT": "Meta", "MSFT": "Microsoft"}
instrument_ids = ["FLPK", "AMAZ", "TT", "NFX", "NVDA", "APL", "GOOG", "MT", "MSFT", ]
purchase_types = ["BUY", "SELL"]
order_submitted = [dt.datetime.now() - dt.timedelta(days=i) for i in range(1, 100)]
sort_by_list = ["Price", "Quantity", "date"]

##creating dataset

results = []
for i in range(500):
    asset_class = random.choice(asset_classes)
    instrument_id = random.choice(instrument_ids)
    counterparty = random.choice(first_names) + " " + random.choice(last_names)
    data_source_name = random.choice(data_source_names)
    results.append(Results(
        assestClass=asset_class,
        countpartyName=counterparty,
        dataSourceName=data_source_name,
        instrumentId=instrument_id,
        instrumentName=instrument_names[instrument_id],
        orderID=str("ORD") + "-" + str(randrange(99999, 1000000)),
        orderSubmitted=random.choice(order_submitted),
        purchaseType=random.choice(purchase_types),
        tradePrice=random.uniform(2, 400),
        tradeQuantity=random.randint(1, 200),

    ))


def sort_trade_by_price(trade, desc):
    sort_by_price = lambda x: x.order_price.price
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


##listing
@app.get('/listing')
async def read_trades(page: int, page_rate: Optional[int] = 10, sort_by: Optional[str] = None,
                      isdesc: Optional[bool] = False):
    page = page - 1
    result_trades = results
    number_of_trades = len(result_trades)

    if number_of_trades == 0:
        return {"status": "failure", "message": "No trades found!!"}, 404
    if page_rate < 0:
        return {"status": "failure", "message": "Oops! Invalid page rate"}, 400
    number_of_pages = ceil(number_of_trades / page_rate)
    if page >= number_of_pages or page < 0:
        return {"status": "failure", "message": "Oops! Page not found"}, 404
    if sort_by:
        result_trades = sortResults(result_trades, sort_by, isdesc)
        if isinstance(result_trades, str):
            return {"status": "failure", "message": "Oops! Invalid sortby property name", "sortbyReceived": sort_by,
                    "sortbyList": sort_by_list}, 400

    result = {
        "page": str(page + 1) + "/" + str(number_of_pages),
        "page_rate": page_rate,
        "total_trades": number_of_trades,
        # "trades": resultTrades[page * page_rate: (page + 1) * page_rate]
        "results": result_trades[page * page_rate:(page + 1) * page_rate]
    }
    return result


@app.get("/trade/{order_Id}")
async def get_trade(order_Id: str):
    result = []
    for trade in results:
        if trade.order_Id == order_Id:
            result = {"status": "success", "trade": trade}
            break
    else:
        return {"status": "failure", "message": "Trade not found"}, 404
    return result


@app.get("/search")
async def search_trade(page: int, search: str, page_rate: Optional[int] = 10, case_sensitive: Optional[bool] = False,
                       sort_by: Optional[str] = None, isdesc: Optional[bool] = False):
    page = page - 1
    if page_rate <= 0:
        return {"status": "failure", "message": "Oops! Invalid page rate"}, 400
    search = search if case_sensitive else search.lower()
    searchResults = []
    for trade in results:
        instrument_id = trade.instrument_id.lower() if not case_sensitive else trade.instrument_id
        instrument_name = trade.instrument_name.lower() if not case_sensitive else trade.instrument_name
        counterparty = trade.counterparty.lower() if not case_sensitive else trade.counterparty
        if search in instrument_id or search in instrument_name or search in counterparty:
            searchResults.append(results)

    number_of_trades = len(searchResults)
    if number_of_trades == 0:
        return {"status": "failure", "message": "No trades found"}, 404

    number_of_pages = ceil(number_of_trades / page_rate)
    if page >= number_of_pages or page < 0:
        return {"status": "failure", "message": "Page not found"}, 404

    if sort_by:
        searchResults = sortResults(searchResults, sort_by, isdesc)
        if isinstance(searchResults, str):
            return {"status": "failure", "message": "Invalid sortby property name", "sortbyReceived": sort_by,
                    "sortbyList": sort_by_list}, 400

    result = {
        "status": "success",
        "page": str(page + 1) + "/" + str(number_of_pages),
        "page_rate": page_rate,
        "total_trades": number_of_trades,
        "trades": searchResults[page * page_rate: (page + 1) * page_rate]
    }
    return result


@app.get("/filter")
async def filter_trades(page: int, page_rate: Optional[int] = 10, asset_class: Optional[str] = None,
                        max_price: Optional[float] = None, min_price: Optional[float] = None,
                        trade_type: Optional[str] = None, sort_by: Optional[str] = None,
                        isdesc: Optional[bool] = False):
    page = page - 1
    if page_rate <= 0:
        return {"status": "failure", "message": "Oops! Invalid page rate"}, 400
    filteredTrades = results

    if asset_class:
        filteredTrades = [trade for trade in filteredTrades if trade.asset_class == asset_class]
    if max_price:
        filteredTrades = [trade for trade in filteredTrades if trade.order_price <= max_price]
    if min_price:
        filteredTrades = [trade for trade in filteredTrades if trade.order_price >= min_price]
    if trade_type:
        filteredTrades = [trade for trade in filteredTrades if trade.purchase_type == trade_type]

    number_of_trades = len(filteredTrades)
    if number_of_trades == 0:
        return {"status": "failure", "message": "No trades found"}, 404
    number_of_pages = ceil(number_of_trades / page_rate)

    if page >= number_of_pages or page < 0:
        return {"status": "failure", "message": "Page not found"}, 404

    if sort_by:
        filteredTrades = sortResults(filteredTrades, sort_by, isdesc)
        if isinstance(filteredTrades, str):
            return {"status": "failure", "message": "Invalid sortby property name", "sortbyReceived": sort_by,
                    "sortbyList": sort_by_list}, 400

    result = {
        "page": str(page + 1) + "/" + str(number_of_pages),
        "page_rate": page_rate,
        "total_trades": number_of_trades,
        "trades": filteredTrades[page * page_rate: (page + 1) * page_rate]
    }
    return result


if __name__ == "__main__":
    uvicorn.run("main:app")
