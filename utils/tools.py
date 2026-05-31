"""
Real tools for agentic AI demos.
All free — no API keys required beyond GEMINI_API_KEY.
"""

import requests


def get_weather(city: str) -> str:
    """
    Get the current weather for any city in the world.

    Args:
        city: Name of the city (e.g. London, New York, Tokyo, Sydney)
    """
    try:
        # Step 1: geocode city → lat/lon
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en", "format": "json"},
            timeout=10,
        ).json()

        if not geo.get("results"):
            return f"City '{city}' not found."

        r = geo["results"][0]
        lat, lon = r["latitude"], r["longitude"]
        name = r["name"]
        country = r.get("country", "")

        # Step 2: get current weather
        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "wind_speed_unit": "kmh",
            },
            timeout=10,
        ).json()

        c = weather["current"]
        temp  = c["temperature_2m"]
        humid = c["relative_humidity_2m"]
        wind  = c["wind_speed_10m"]

        return (
            f"{name}, {country}: {temp}°C, "
            f"humidity {humid}%, wind {wind} km/h"
        )
    except Exception as e:
        return f"Weather lookup failed: {e}"


def get_stock_price(ticker: str) -> str:
    """
    Get the latest stock price for a ticker symbol.

    Args:
        ticker: Stock ticker symbol (e.g. AAPL, GOOGL, TSLA, MSFT, AMZN)
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker.upper())
        info  = stock.fast_info
        price = info.last_price
        currency = getattr(info, "currency", "USD")
        prev  = getattr(info, "previous_close", None)
        change = ""
        if prev:
            pct = ((price - prev) / prev) * 100
            change = f"  ({'+' if pct >= 0 else ''}{pct:.2f}% today)"
        return f"{ticker.upper()}: {price:.2f} {currency}{change}"
    except Exception as e:
        return f"Stock lookup failed for '{ticker}': {e}"


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert a value between units of volume, length, or weight.

    Supported volume units : gallon, litre, liter, ml, cup, pint, quart, fl oz
    Supported length units : mile, km, meter, foot, feet, inch, cm, yard
    Supported weight units : kg, gram, lb, pound, ounce, oz, tonne, ton

    Args:
        value: The numeric value to convert
        from_unit: Unit to convert from (e.g. gallons, km, feet)
        to_unit: Unit to convert to (e.g. litres, miles, meters)
    """
    # All conversions normalised to a base unit
    to_litre = {
        "gallon": 3.78541, "gallons": 3.78541,
        "litre": 1.0, "litres": 1.0, "liter": 1.0, "liters": 1.0, "l": 1.0,
        "ml": 0.001, "millilitre": 0.001, "millilitres": 0.001,
        "cup": 0.236588, "cups": 0.236588,
        "pint": 0.473176, "pints": 0.473176,
        "quart": 0.946353, "quarts": 0.946353,
        "fl oz": 0.0295735, "fluid ounce": 0.0295735, "fluid ounces": 0.0295735,
    }
    to_metre = {
        "meter": 1.0, "meters": 1.0, "metre": 1.0, "metres": 1.0, "m": 1.0,
        "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
        "kilometre": 1000.0, "kilometres": 1000.0,
        "mile": 1609.34, "miles": 1609.34,
        "foot": 0.3048, "feet": 0.3048, "ft": 0.3048,
        "inch": 0.0254, "inches": 0.0254,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "yard": 0.9144, "yards": 0.9144,
    }
    to_kg = {
        "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
        "g": 0.001, "gram": 0.001, "grams": 0.001,
        "lb": 0.453592, "lbs": 0.453592, "pound": 0.453592, "pounds": 0.453592,
        "oz": 0.0283495, "ounce": 0.0283495, "ounces": 0.0283495,
        "tonne": 1000.0, "metric ton": 1000.0,
        "ton": 907.185, "tons": 907.185, "short ton": 907.185,
    }

    f = from_unit.lower().strip()
    t = to_unit.lower().strip()

    for table, category in [(to_litre, "volume"), (to_metre, "length"), (to_kg, "weight")]:
        if f in table and t in table:
            result = value * table[f] / table[t]
            return f"{value} {from_unit} = {result:.4f} {to_unit}  ({category})"

    return (
        f"Cannot convert '{from_unit}' to '{to_unit}'. "
        "Supported categories: volume, length, weight. "
        "Check spelling — use singular or plural forms."
    )


def get_country_info(country: str) -> str:
    """
    Get key facts about a country: capital, population, region, currency, and languages.

    Args:
        country: Full or partial country name (e.g. France, Japan, United States, Australia)
    """
    try:
        resp = requests.get(
            f"https://restcountries.com/v3.1/name/{country}",
            params={"fields": "name,capital,population,region,subregion,currencies,languages,flags"},
            timeout=10,
        )
        if resp.status_code != 200:
            return f"Country '{country}' not found."

        data = resp.json()[0]
        name      = data["name"]["common"]
        capital   = ", ".join(data.get("capital", ["N/A"]))
        population = f"{data['population']:,}"
        region    = data.get("subregion") or data.get("region", "N/A")
        currencies = ", ".join(
            f"{v['name']} ({k})" for k, v in data.get("currencies", {}).items()
        )
        languages = ", ".join(data.get("languages", {}).values())

        return (
            f"{name} | Capital: {capital} | Population: {population} | "
            f"Region: {region} | Currency: {currencies} | Languages: {languages}"
        )
    except Exception as e:
        return f"Country lookup failed: {e}"


def get_public_holidays(country_code: str, year: int) -> str:
    """
    Get the list of public holidays for a country in a given year.

    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. US, GB, AU, IN, DE, FR, JP)
        year: The year to get holidays for (e.g. 2025, 2026)
    """
    try:
        resp = requests.get(
            f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code.upper()}",
            timeout=10,
        )
        if resp.status_code != 200:
            return f"No holiday data found for country code '{country_code}' in {year}."

        holidays = resp.json()
        if not holidays:
            return f"No public holidays found for {country_code.upper()} in {year}."

        lines = [f"{h['date']}  {h['name']}" for h in holidays]
        return f"Public holidays in {country_code.upper()} ({year}):\n" + "\n".join(lines)
    except Exception as e:
        return f"Holiday lookup failed: {e}"


def get_random_joke() -> str:
    """
    Fetch a random joke. Use this as a fun fallback when no other tool applies.
    """
    try:
        resp = requests.get(
            "https://official-joke-api.appspot.com/random_joke",
            timeout=10,
        ).json()
        return f"{resp['setup']}\n...{resp['punchline']}"
    except Exception as e:
        return f"Why did the API fail? Because it had too many requests! (real error: {e})"
