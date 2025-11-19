"""
@fileoverview
Provides live weather and pollen data for the Data Cleaners dashboard.
Fetches current forecast (temperature, humidity, wind speed, and precipitation)
from DMI or falls back to Open-Meteo. Returns structured JSON for the frontend.
"""

import sys, os
sys.path.insert(0, os.getcwd())

import requests
from private_settings import DMI_API_KEY


# ============================================================================
# MAIN WEATHER FETCH FUNCTION
# ============================================================================
def get_weather_data():
    """
    Fetches live weather and pollen data for the dashboard.

    Why:
        To provide temperature, humidity, wind speed, and rain data for
        contextual AI suggestions (e.g., rescheduling cleaning on rainy days).

    How:
        1. Try DMI Gateway API using API key.
        2. If unavailable, fall back to Open-Meteo (no key required).
        3. Add placeholder pollen levels for display.

    Returns:
        dict: Structured JSON with provider, coordinates, weather values,
              and pollen levels.
    """
    # Default location: Aalborg (for demonstration and testing)
    lat, lon = 57.0488, 9.9217

    try:
        # --------------------------------------------------------------------
        # 🔹 PRIMARY SOURCE: DMI Gateway API
        # --------------------------------------------------------------------
        url = f"https://dmigatewayapi.dmi.dk/v1/forecast?lat={lat}&lon={lon}&apikey={DMI_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract the first forecast entry (represents current conditions)
        first_entry = data.get("timeseries", [])[0]
        details = first_entry.get("data", {}).get("instant", {}).get("details", {}) if first_entry else {}

        temperature = details.get("air_temperature")
        humidity = details.get("relative_humidity")
        wind_speed = details.get("wind_speed")
        rain = details.get("precipitation_rate") or details.get("precipitation_amount", 0)

        # --------------------------------------------------------------------
        # Mock pollen data (placeholder until live API is integrated)
        # --------------------------------------------------------------------
        pollen_data = {
            "Birch": "Low",
            "Grass": "Moderate",
            "Mugwort": "None"
        }

        # Build and return structured result
        return {
            "provider": "DMI",
            "coords": {"lat": lat, "lon": lon},
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "rain": rain,
            "pollen": pollen_data
        }

    except Exception as e:
        print(f"DMI fetch failed: {e}")

        # --------------------------------------------------------------------
        # 🔸 FALLBACK SOURCE: Open-Meteo API (no API key required)
        # --------------------------------------------------------------------
        try:
            fallback_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation"
            )
            fallback_response = requests.get(fallback_url, timeout=10)
            fallback_response.raise_for_status()
            fallback_data = fallback_response.json()

            current = fallback_data.get("current", {})
            temperature = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            wind_speed = current.get("wind_speed_10m")
            rain = current.get("precipitation")

            pollen_data = {
                "Birch": "Low",
                "Grass": "Low",
                "Mugwort": "None"
            }

            return {
                "provider": "Open-Meteo",
                "coords": {"lat": lat, "lon": lon},
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "rain": rain,
                "pollen": pollen_data,
                "note": f"DMI unavailable → fallback used ({type(e).__name__})"
            }

        except Exception as fallback_error:
            # Final fail-safe: send readable error for frontend
            return {
                "error": f"Could not fetch weather data from either source: {fallback_error}"
            }
