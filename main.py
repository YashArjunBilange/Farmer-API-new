from fastapi import FastAPI, Query
from enum import Enum
import requests
import os

app = FastAPI(title="Farmer Market Price API")

BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = os.environ.get("DATA_GOV_API_KEY")  # <- set this in Railway, DO NOT hardcode

class CommodityEnum(str, Enum):
    Potato = "Potato"
    Onion = "Onion"
    Tomato = "Tomato"
    Banana = "Banana"
    Mango = "Mango"

class StateEnum(str, Enum):
    Maharashtra = "Maharashtra"

class MarketEnum(str, Enum):
    Nashik = "Nashik"
    Pune = "Pune"
    Jalgaon = "Jalgaon"

@app.get("/")
def root():
    return {"message": "Farmer Market Price API — visit /docs"}

@app.get("/price")
def get_price(
    commodity: CommodityEnum = Query(..., description="Choose commodity"),
    state: StateEnum = Query(StateEnum.Maharashtra, description="Choose state"),
    market: MarketEnum = Query(MarketEnum.Nashik, description="Choose market"),
):
    if not API_KEY:
        return {"error": "Server misconfigured: DATA_GOV_API_KEY not set"}

    params = {
        "api-key": API_KEY,
        "format": "json",
        "filters[commodity]": commodity.value,
        "filters[state]": state.value,
        "filters[market]": market.value,
        "limit": 1,
    }

    try:
        resp = requests.get(BASE_URL, params=params, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        if "records" not in data or len(data["records"]) == 0:
            return {"error": f"No price data found for {commodity.value} in {market.value}, {state.value}"}
        rec = data["records"][0]
        return {
            "commodity": rec.get("commodity"),
            "state": rec.get("state"),
            "district": rec.get("district"),
            "market": rec.get("market"),
            "arrival_date": rec.get("arrival_date"),
            "min_price": rec.get("min_price"),
            "max_price": rec.get("max_price"),
            "modal_price": rec.get("modal_price"),
        }
    except requests.exceptions.RequestException as e:
        return {"error": "Upstream request failed", "detail": str(e)}
    except Exception as e:
        return {"error": "Server error", "detail": str(e)}
