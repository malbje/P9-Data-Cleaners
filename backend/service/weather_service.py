# backend/service/weather_service.py
"""
Wrapper around backend/service/weather.py
Used to expose weather data to the Flask app without modifying the core weather module.
This keeps integration lightweight and maintainable.
"""

# Import the function that handles IP lookup and API calls
from backend.service.weather import get_weather_for_current_ip

def get_weather_data():
    """
    Fetch weather observations and forecast based on current IP location.
    Returns a simplified dictionary suitable for frontend widgets.
    
    Why:
        Separate "integration" concerns from core weather logic. The frontend and Flask
        should receive a clean, predictable structure no matter the provider (DMI/Open-Meteo).
    How:
        Delegates to get_weather_for_current_ip(), then normalizes keys.
    """
    result = get_weather_for_current_ip()

    # Graceful failure path so the API returns JSON with an error, not a 500
    if not result:
        return {"error": "Unable to fetch weather data"}

    # Extract and normalize fields for the widget
    lat, lon = result.get("coords", (None, None))
    forecast = result.get("forecast", {}) or {}
    provider = forecast.get("provider", "unknown")

    return {
        "coords": {"lat": lat, "lon": lon},
        "provider": provider,
        "forecast": forecast.get("data", {}),
        "observations": result.get("observations", {}),
    }
