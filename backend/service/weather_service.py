import sys, os
sys.path.insert(0, os.getcwd())

from private_settings import DMI_API_KEY
from backend.service.weather import get_weather_for_current_ip, get_7day_forecast_by_coords, get_location_from_ip

if __name__ == "__main__":
    coords = get_location_from_ip()
    lat, lon = coords
    fc = get_7day_forecast_by_coords(lat, lon, DMI_API_KEY)
    print(fc)
    if fc.get("provider") == "open-meteo":
        daily = fc["data"].get("daily", {})
        dates = daily.get("time", [])
        temps_max = daily.get("temperature_2m_max", [])
        temps_min = daily.get("temperature_2m_min", [])
        print("7-day forecast (Open-Meteo):")
        for d, tmax, tmin in zip(dates, temps_max, temps_min):
            print(f"  {d}: max {tmax}°C, min {tmin}°C")

