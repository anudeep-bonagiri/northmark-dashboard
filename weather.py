import datetime
import numpy as np
import pandas as pd
import requests_cache
import openmeteo_requests
from retry_requests import retry


class WeatherClient:
    """Encapsulate Open-Meteo requests + interpolation logic.

    Usage:
        wc = WeatherClient(selected_date="2025-08-15", units="metric")
        epochs = wc.generate_target_epochs(num_points)
        w = wc.get_weather_at_time(lat, lon, target_epoch)
    """

    def __init__(self, selected_date="2025-08-15", units="metric", cache_path=".cache"):
        self.selected_date = selected_date
        self.units = units

        # configure cached session + retry wrapper
        cache_session = requests_cache.CachedSession(cache_path, expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)

    def generate_target_epochs(self, num_points, start_hour_utc=20, window_hours=2):
        """Return an array of epoch seconds evenly spaced across the 2-hour window.

        Default maps 15:00-17:00 CDT (UTC-5) to 20:00-22:00 UTC using the
        selected_date stored on the client.
        """
        # Parse the selected date and compute UTC window
        start_ts = int(datetime.datetime.fromisoformat(self.selected_date).replace(tzinfo=datetime.timezone.utc).timestamp())
        window_start = start_ts + (start_hour_utc * 3600)
        window_end = window_start + (window_hours * 3600)

        total_seconds = window_end - window_start
        total_minutes = total_seconds // 60
        if total_minutes >= num_points:
            minute_offsets = np.linspace(0, total_minutes - 1, num=num_points, endpoint=True).astype(int)
            return (window_start + (minute_offsets * 60)).astype(int)
        else:
            return np.linspace(window_start, window_end - 1, num=num_points, endpoint=True).astype(int)

    def get_weather_at_time(self, lat, lon, target_epoch, units=None):
        """Fetch hourly arrays from Open-Meteo and interpolate to target_epoch.

        Returns a dict structured like {"current": {...}} on success or an
        error dict with keys 'error' and 'message'.
        """
        units = units or self.units
        url = "https://api.open-meteo.com/v1/forecast"
        start_date = self.selected_date
        end_date = (datetime.datetime.fromisoformat(start_date) + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join([
                "temperature_2m",
                "relativehumidity_2m",
                "windspeed_10m",
                "winddirection_10m",
                "precipitation",
                "pressure_msl",
            ]),
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "UTC",
        }

        try:
            responses = self.client.weather_api(url, params=params)
            if not responses:
                return {"error": "no_response", "message": "open-meteo returned no responses"}

            response = responses[0]
            hourly = response.Hourly()

            # Robust time parsing
            raw_times = hourly.Time()
            try:
                times = np.atleast_1d(np.array(raw_times, dtype=float))
            except Exception:
                try:
                    times = np.array(pd.to_datetime(list(raw_times), utc=True).view('int64') // 10**9, dtype=float)
                except Exception:
                    times = np.atleast_1d(np.array(raw_times, dtype=float))

            temp = np.atleast_1d(np.array(hourly.Variables(0).ValuesAsNumpy(), dtype=float))
            rh = np.atleast_1d(np.array(hourly.Variables(1).ValuesAsNumpy(), dtype=float))
            ws = np.atleast_1d(np.array(hourly.Variables(2).ValuesAsNumpy(), dtype=float))
            wd = np.atleast_1d(np.array(hourly.Variables(3).ValuesAsNumpy(), dtype=float))
            precip = np.atleast_1d(np.array(hourly.Variables(4).ValuesAsNumpy(), dtype=float))
            pressure = np.atleast_1d(np.array(hourly.Variables(5).ValuesAsNumpy(), dtype=float))

            # Debug: console output (keeps original behavior)
            print(f"target_epoch={target_epoch}, times[0]={times[0]}, times[-1]={times[-1]}")
            print(f"sample temp values: {temp[:3]}")

            if times.size == 0 or temp.size == 0:
                return {"error": "no_hourly_data", "message": "Open-Meteo returned empty hourly arrays"}

            if target_epoch <= times[0]:
                idx = 0
                return {"current": {"temp": float(temp[idx]), "humidity": float(rh[idx]), "wind_speed": float(ws[idx]), "wind_dir": float(wd[idx]), "precip": float(precip[idx]), "pressure": float(pressure[idx])}}
            if target_epoch >= times[-1]:
                idx = -1
                return {"current": {"temp": float(temp[idx]), "humidity": float(rh[idx]), "wind_speed": float(ws[idx]), "wind_dir": float(wd[idx]), "precip": float(precip[idx]), "pressure": float(pressure[idx])}}

            try:
                temp_val = float(np.interp(target_epoch, times, temp))
                rh_val = float(np.interp(target_epoch, times, rh))
                ws_val = float(np.interp(target_epoch, times, ws))
                wd_val = float(np.interp(target_epoch, times, wd))
                precip_val = float(np.interp(target_epoch, times, precip))
                pressure_val = float(np.interp(target_epoch, times, pressure))
            except Exception as e:
                return {"error": "interp_error", "message": str(e)}

            return {"current": {"temp": temp_val, "humidity": rh_val, "wind_speed": ws_val, "wind_dir": wd_val, "precip": precip_val, "pressure": pressure_val}}

        except Exception as e:
            return {"error": "exception", "message": str(e)}
