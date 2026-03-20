import re
import requests
from concurrent.futures import ThreadPoolExecutor
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

YF_HEADERS = {"User-Agent": "Mozilla/5.0"}
WGB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Origin": "http://www.worldgovernmentbonds.com",
    "Referer": "http://www.worldgovernmentbonds.com/country/india/",
}


def _yf_price(symbol):
    """Fetch latest price for a Yahoo Finance symbol."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    r = requests.get(url, headers=YF_HEADERS, timeout=8)
    r.raise_for_status()
    meta = r.json()["chart"]["result"][0]["meta"]
    return meta.get("regularMarketPrice")


def _get_usd_inr():
    """Return current USD→INR rate from frankfurter.app."""
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=INR",
            timeout=8,
        )
        return r.json().get("rates", {}).get("INR")
    except Exception:
        return None


def _fetch_commodities(usd_inr):
    """Gold, Silver, Crude Oil from Yahoo Finance – converted to INR."""
    result = {"gold": None, "silver": None, "oil": None}
    mapping = {"gold": "GC=F", "silver": "SI=F", "oil": "CL=F"}
    for key, sym in mapping.items():
        try:
            price = _yf_price(sym)
            if price is not None:
                price_usd = float(price)
                # Convert to INR (per troy oz for gold/silver, per barrel for oil)
                if usd_inr:
                    result[key] = round(price_usd * usd_inr, 2)
                else:
                    result[key] = round(price_usd, 2)
        except Exception:
            pass
    return result


def _fetch_currencies():
    """Currency rates from frankfurter.app (free, no API key)."""
    result = {"usd_inr": None, "eur_inr": None, "gbp_inr": None}
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=INR,EUR,GBP",
            timeout=8,
        )
        data = r.json()
        rates = data.get("rates", {})
        usd_inr = rates.get("INR")
        eur_val = rates.get("EUR")
        gbp_val = rates.get("GBP")
        result["usd_inr"] = round(usd_inr, 2) if usd_inr else None
        result["eur_inr"] = round(usd_inr / eur_val, 2) if usd_inr and eur_val else None
        result["gbp_inr"] = round(usd_inr / gbp_val, 2) if usd_inr and gbp_val else None
    except Exception:
        pass
    return result


def _fetch_bonds():
    """Indian Government Bond yields from WorldGovernmentBonds.com API."""
    result = {"india_10y": None, "india_5y": None, "india_2y": None}
    try:
        payload = {
            "GLOBALVAR": {
                "JS_VARIABLE": "jsGlobalVars",
                "FUNCTION": "Country",
                "DOMESTIC": True,
                "ENDPOINT": "http://www.worldgovernmentbonds.com/wp-json/country/v1/historical",
                "DATE_RIF": "2099-12-31",
                "OBJ": None,
                "COUNTRY1": {
                    "SYMBOL": "8",
                    "PAESE": "India",
                    "PAESE_UPPERCASE": "INDIA",
                    "BANDIERA": "in",
                    "URL_PAGE": "india",
                },
                "COUNTRY2": None,
                "OBJ1": None,
                "OBJ2": None,
            }
        }
        r = requests.post(
            "https://www.worldgovernmentbonds.com/wp-json/country/v1/main",
            json=payload,
            headers=WGB_HEADERS,
            timeout=10,
        )
        data = r.json()

        # 10Y yield comes as a direct field
        bond10y = data.get("bond10y")
        if bond10y is not None:
            result["india_10y"] = float(bond10y)

        # Parse 5Y and 2Y from the bondPrices HTML table
        html = data.get("bondPrices", "")
        # Pattern: maturity text → yield text  e.g.  "5 years" ... "6.484%"
        rows = re.findall(
            r'(\d+)\s+years?\s*</a>\s*</td>\s*<td[^>]*>\s*([\d.]+)%',
            html,
            re.DOTALL | re.IGNORECASE,
        )
        for maturity, yld in rows:
            m = int(maturity)
            if m == 5:
                result["india_5y"] = float(yld)
            elif m == 2:
                result["india_2y"] = float(yld)
    except Exception:
        pass
    return result


# ── Keep the old currency-only endpoint working ──
@api_view(["GET"])
def currency_rates(request):
    data = _fetch_currencies()
    return Response(data)


# ── Unified endpoint: all market data in one call ──
@api_view(["GET"])
def market_data(request):
    try:
        # Fetch USD/INR first (needed for commodity conversion)
        usd_inr = _get_usd_inr()

        with ThreadPoolExecutor(max_workers=3) as pool:
            f_comm = pool.submit(_fetch_commodities, usd_inr)
            f_curr = pool.submit(_fetch_currencies)
            f_bond = pool.submit(_fetch_bonds)
        return Response({
            "commodities": f_comm.result(),
            "currencies": f_curr.result(),
            "bonds": f_bond.result(),
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
