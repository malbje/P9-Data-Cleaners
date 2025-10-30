"""Weather utilities (DMI + fallback) for the backend.

This module provides functions to:
- resolve approximate coordinates from the machine's public IP
- call DMI (DMIGW) endpoints for observations
- obtain a 7-day forecast (DMI preferred, Open-Meteo fallback)
- validate runtime environment for required deps and keys

Naming convention:
- File and function names are "atomic" (single responsibility) so each name clearly reflects what it does.
- All functions use Google-style docstrings to make the behavior explicit for other developers.
"""

try:
    import requests  # type: ignore
    REQUESTS_AVAILABLE = True
except Exception:
    requests = None  # type: ignore
    REQUESTS_AVAILABLE = False

from typing import Tuple, Dict, Optional, Any
import sys, os
# Ensure project root is on sys.path so "import private_settings" works when running this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import private_settings


def _ensure_requests_available():
    """
    Ensure the 'requests' package is available.

    Raises:
        RuntimeError: If the 'requests' package is not installed in the active environment.

    Notes:
        Provides a clear action message to install the dependency and to select the correct
        Python interpreter in editors like VS Code.
    """
    if not REQUESTS_AVAILABLE:
        raise RuntimeError(
            "Missing required package 'requests'. Install it in the active environment:\n"
            "  pip install requests\n"
            "Then ensure VS Code uses the same Python interpreter (Ctrl+Shift+P → Python: Select Interpreter)."
        )


BASE_DMI_URL = "https://dmigw.govcloud.dk"
# Fallback DMI API key (use only if private_settings.DMI_API_KEY is not set)
from private_settings import DMI_API_KEY
FALLBACK_DMI_KEY = DMI_API_KEY


def get_location_from_ip(ip_api_url: str = "https://ipinfo.io/json") -> Optional[Tuple[float, float]]:
    """
    Get approximate geographic coordinates (latitude, longitude) for the current machine's public IP.

    Args:
        ip_api_url (str): URL of the IP geolocation service that returns JSON with a 'loc' field
                          (format: 'lat,lon'). Defaults to "https://ipinfo.io/json".

    Returns:
        tuple[float, float] or None: (latitude, longitude) on success, otherwise None.

    Raises:
        RuntimeError: If 'requests' is not available in the environment.
    """
    # Ensure requests is available before performing HTTP calls
    _ensure_requests_available()
    try:
        resp = requests.get(ip_api_url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        loc = data.get("loc")
        if not loc:
            return None
        lat_str, lon_str = loc.split(",")
        return float(lat_str), float(lon_str)
    except Exception:
        return None


def _get_dmi_api_key(api_key: Optional[str]) -> Optional[str]:
    """
    Resolve which DMI API key to use.

    Order of precedence:
      1) explicit `api_key` argument
      2) private_settings.DMI_API_KEY
      3) module fallback key (FALLBACK_DMI_KEY)

    Args:
        api_key (str|None): Explicit API key to use (overrides private_settings).

    Returns:
        str|None: API key string if available, else None.
    """
    if api_key:
        return api_key
    key = getattr(private_settings, "DMI_API_KEY", None)
    if key:
        return key
    return FALLBACK_DMI_KEY


def dmi_request(path: str, params: Optional[Dict[str, Any]] = None, api_key: Optional[str] = None, timeout: int = 10) -> Optional[Dict]:
    """
    Generic helper to call a DMIGW endpoint with the required header.

    Args:
        path (str): Path on the DMI gateway (e.g. "/v2/metObs").
        params (dict|None): Query parameters for the GET request.
        api_key (str|None): API key to use (overrides private_settings).
        timeout (int): Request timeout in seconds.

    Returns:
        dict|None: Parsed JSON response on success, otherwise None.

    Raises:
        RuntimeError: If 'requests' is not available.
    """
    # Ensure requests is available before performing HTTP calls
    _ensure_requests_available()
    key = _get_dmi_api_key(api_key)
    if not key:
        return None
    url = BASE_DMI_URL.rstrip("/") + "/" + path.lstrip("/")
    headers = {"X-Gravitee-Api-Key": key}
    try:
        resp = requests.get(url, params=params or {}, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def get_metobs_by_coords(lat: float, lon: float, radius_km: float = 10.0, elements: Optional[str] = None, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Request recent meteorological observations from DMIGW near the provided coordinates.

    Args:
        lat (float): Latitude of the search center.
        lon (float): Longitude of the search center.
        radius_km (float): Search radius in kilometers (default: 10.0).
        elements (str|None): Comma-separated observation elements to request (e.g. "temperature,windSpeed").
        api_key (str|None): Optional DMI API key to override private_settings.

    Returns:
        dict|None: Raw JSON response from DMIGW (observations) or None on failure.

    Notes:
        Parameter names used in the request are the common ones; adapt if your gateway differs.
    """
    # The DMIGW metObs endpoint accepts different parameters depending on the gateway setup.
    # Common useful parameters: lat, lon, distance/radius, elements, limit.
    params = {
        "lat": lat,
        "lon": lon,
        "radius": radius_km,
        "limit": 50
    }
    if elements:
        params["elements"] = elements
    return dmi_request("/v2/metObs", params=params, api_key=api_key)


def get_7day_forecast_by_coords(lat: float, lon: float, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Obtain a 7-day forecast for the given coordinates.

    The function prefers a DMI forecast endpoint; if that fails it falls back to Open-Meteo.

    Args:
        lat (float): Latitude.
        lon (float): Longitude.
        api_key (str|None): Optional DMI API key to override private_settings.

    Returns:
        dict|None: A dictionary with keys:
            - 'provider': "dmi" or "open-meteo"
            - 'data': raw provider JSON
        Returns None if both DMI and fallback fail.
    """
    # Ensure requests is available before performing HTTP calls
    _ensure_requests_available()
    # Try a likely DMI forecast endpoint first (may need tuning to your gateway).
    dmi_resp = dmi_request("/v2/forecasts", params={"lat": lat, "lon": lon, "limit": 7}, api_key=api_key)
    if dmi_resp:
        return {"provider": "dmi", "data": dmi_resp}

    # Fallback to Open-Meteo for 7-day forecast
    try:
        om_url = "https://api.open-meteo.com/v1/forecast"
        om_params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "timezone": "auto",
            "forecast_days": 7
        }
        resp = requests.get(om_url, params=om_params, timeout=10)
        resp.raise_for_status()
        return {"provider": "open-meteo", "data": resp.json()}
    except Exception:
        return None


def get_weather_for_current_ip(api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Determine current public IP location and return observations plus a 7-day forecast.

    Args:
        api_key (str|None): Optional DMI API key to override private_settings.

    Returns:
        dict|None: {
            "coords": (lat, lon),
            "observations": <raw observations JSON or None>,
            "forecast": <forecast JSON or None>
        } or None if location detection fails.
    """
    coords = get_location_from_ip()
    if coords is None:
        return None
    lat, lon = coords
    obs = get_metobs_by_coords(lat, lon, api_key=api_key)
    forecast = get_7day_forecast_by_coords(lat, lon, api_key=api_key)
    return {"coords": coords, "observations": obs, "forecast": forecast}


def validate_environment() -> Dict[str, Any]:
    """
    Quick environment validation for the weather module.

    Returns:
        dict: {
            "requests_installed": bool,
            "dmi_key_present": bool,
            "dmi_key_source": "private_settings"|"fallback"|None
        }
    """
    status = {"requests_installed": REQUESTS_AVAILABLE, "dmi_key_present": False, "dmi_key_source": None}
    dmi_key = getattr(private_settings, "DMI_API_KEY", None)
    if dmi_key:
        status["dmi_key_present"] = True
        status["dmi_key_source"] = "private_settings"
    elif FALLBACK_DMI_KEY:
        status["dmi_key_present"] = True
        status["dmi_key_source"] = "fallback"
    return status


if __name__ == "__main__":
    # Diagnostic: show which Python executable and virtualenv (if any) is being used
    print("Python executable (used to run this script):", sys.executable)
    print("VIRTUAL_ENV environment variable:", os.environ.get("VIRTUAL_ENV"))

    # Quick demo: detect coords and print observations + short forecast summary
    env = validate_environment()
    print("Environment check:", env)
    # If requests missing, show the helpful message and stop
    if not env["requests_installed"]:
        print("Install 'requests' in the active environment (pip install requests) and ensure VS Code uses that interpreter.")
    else:
        coords = get_location_from_ip()
        print("Detected coords:", coords)
        dmi_key = getattr(private_settings, "DMI_API_KEY", None)
        if not dmi_key and not FALLBACK_DMI_KEY:
            print("No DMI API key found in private_settings.DMI_API_KEY and no fallback key available. DMI calls will be skipped.")
        if coords:
            lat, lon = coords
            obs = None
            if env["dmi_key_present"]:
                obs = get_metobs_by_coords(lat, lon, elements="temperature,windSpeed,precipitation", api_key=dmi_key)
            print("Observations (raw):", obs)
            fc = get_7day_forecast_by_coords(lat, lon, api_key=dmi_key)
            if fc:
                if fc.get("provider") == "open-meteo":
                    daily = fc["data"].get("daily", {})
                    dates = daily.get("time", [])
                    temps_max = daily.get("temperature_2m_max", [])
                    temps_min = daily.get("temperature_2m_min", [])
                    print("7-day forecast (Open-Meteo):")
                    for d, tmax, tmin in zip(dates, temps_max, temps_min):
                        print(f"  {d}: max {tmax}°C, min {tmin}°C")
                else:
                    print("7-day forecast (DMI raw):", fc["data"])
            else:
                print("Failed to fetch forecast (DMI and fallback failed).")
        else:
            print("Failed to detect location from IP.")
