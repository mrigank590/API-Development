import datetime as dt
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI()

# Mocked database
database = [
    {
        "tradeId": "1",
        "assetClass": "Equity",
        "counterparty": "ABC Corp",
        "instrumentId": "AAPL",
        "instrumentName": "Apple Inc.",
        "tradeDateTime": dt.datetime(2023, 6, 1, 10, 0),
        "tradeDetails": {
            "buySellIndicator": "BUY",
            "price": 150.0,
            "quantity": 100
        },
        "trader": "John Doe"
    },
    {
        "tradeId": "2",
        "assetClass": "Bond",
        "counterparty": "XYZ Bank",
        "instrumentId": "TSLA",
        "instrumentName": "Tesla Inc.",
        "tradeDateTime": dt.datetime(2023, 7, 11, 14, 30),
        "tradeDetails": {
            "buySellIndicator": "SELL",
            "price": 800.0,
            "quantity": 50
        },
        "trader": "Jane Smith"
    },
    {
        "tradeId": "3",
        "assetClass": "Equity",
        "counterparty": "ABC Corp",
        "instrumentId": "AAPL",
        "instrumentName": "Apple Inc.",
        "tradeDateTime": dt.datetime(2023, 6, 10, 10, 0),
        "tradeDetails": {
            "buySellIndicator": "BUY",
            "price": 90.0,
            "quantity": 100
        },
        "trader": "John"
    },
    # Add more trades here...
]


class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")
    price: float = Field(description="The price of the Trade.")
    quantity: int = Field(description="The amount of units traded.")

class Trade(BaseModel):
    assetClass: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")
    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")
    instrumentId: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")
    instrumentName: str = Field(alias="instrumentName", description="The name of the instrument traded.")
    tradeDateTime: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")
    tradeDetails: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")
    tradeId: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")
    trader: str = Field(description="The name of the Trader")

@app.get("/trades", response_model=List[Trade])
def get_trades(
    search: Optional[str] = Query(None, description="Search text across fields"),
    assetClass: Optional[str] = Query(None, description="Asset class of the trade"),
    start: Optional[dt.datetime] = Query(None, description="Minimum date for tradeDateTime"),
    end: Optional[dt.datetime] = Query(None, description="Maximum date for tradeDateTime"),
    minPrice: Optional[float] = Query(None, description="Minimum value for tradeDetails.price"),
    maxPrice: Optional[float] = Query(None, description="Maximum value for tradeDetails.price"),
    tradeType: Optional[str] = Query(None, description="Trade type (BUY or SELL)"),
    sort: Optional[str] = Query(None, description="Field to sort by")
):
    trades = database

    if search:
        trades = [trade for trade in trades if search.lower() in str(trade).lower()]

    if assetClass:
        trades = [trade for trade in trades if trade.get("assetClass") == assetClass]

    if start:
        trades = [trade for trade in trades if trade.get("tradeDateTime") >= start]

    if end:
        trades = [trade for trade in trades if trade.get("tradeDateTime") <= end]

    if minPrice:
        trades = [trade for trade in trades if trade.get("tradeDetails").get("price") >= minPrice]

    if maxPrice:
        trades = [trade for trade in trades if trade.get("tradeDetails").get("price") <= maxPrice]

    if tradeType:
        trades = [trade for trade in trades if trade.get("tradeDetails").get("buySellIndicator") == tradeType.upper()]


    if sort:
        reverse = False
        if sort.startswith("-"):
            reverse = True
            sort = sort[1:]

        if sort == "tradeDetails.price":
            trades = sorted(trades, key=lambda x: x.get("tradeDetails").get("price"), reverse=reverse)
        elif sort == "tradeDetails.quantity":
            trades = sorted(trades, key=lambda x: x.get("tradeDetails").get("quantity"), reverse=reverse)
        else:
            trades = sorted(trades, key=lambda x: x.get(sort, ""), reverse=reverse)

    return trades

@app.get("/trades/{trade_id}", response_model=Trade)
def get_trade_by_id(trade_id: str):
    trade = next((trade for trade in database if trade.get("tradeId") == trade_id), None)
    if trade:
        return trade
    raise HTTPException(status_code=404, detail="Trade not found")
