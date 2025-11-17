import datetime
import json
import logging
import os
import requests

from azure.storage.blob import BlobServiceClient
import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    logger = logging.getLogger("FetchWeather")
    logger.setLevel(logging.INFO)

    lat = os.getenv("WEATHER_LAT")
    lon = os.getenv("WEATHER_LON")
    container = os.getenv("DATA_CONTAINER", "weather-data")
    storage_conn = os.getenv("AzureWebJobsStorage")
    user_agent = os.getenv("WEATHER_USER_AGENT", "wxdemo/1.0 (someone@example.com)")

    if not (lat and lon and storage_conn):
        logger.error("Missing required settings. Check WEATHER_LAT, WEATHER_LON, and AzureWebJobsStorage.")
        return

    headers = {
        "User-Agent": user_agent,
        "Accept": "application/geo+json"
    }

    try:
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        r_points = requests.get(points_url, headers=headers, timeout=20)
        r_points.raise_for_status()
        props = r_points.json().get("properties", {})

        forecast_url = props.get("forecast")
        hourly_url = props.get("forecastHourly")
        alerts_url = f"https://api.weather.gov/alerts?active=1&point={lat},{lon}"

        data = {"meta": {"lat": lat, "lon": lon, "utc": datetime.datetime.utcnow().isoformat() + "Z"}}

        if forecast_url:
            r_forecast = requests.get(forecast_url, headers=headers, timeout=20)
            r_forecast.raise_for_status()
            data["forecast"] = r_forecast.json()

        if hourly_url:
            r_hourly = requests.get(hourly_url, headers=headers, timeout=20)
            r_hourly.raise_for_status()
            data["forecastHourly"] = r_hourly.json()

        r_alerts = requests.get(alerts_url, headers=headers, timeout=20)
        r_alerts.raise_for_status()
        data["alerts"] = r_alerts.json()

        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        blob_name = f"{lat},{lon}/{ts}/weather.json"

        blob_service = BlobServiceClient.from_connection_string(storage_conn)
        container_client = blob_service.get_container_client(container)
        try:
            container_client.create_container()
        except Exception:
            pass

        container_client.upload_blob(
            name=blob_name,
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            overwrite=True,
            content_type="application/json"
        )

        logger.info(f"Saved weather data to blob: {blob_name}")

    except requests.HTTPError as e:
        logger.error(f"HTTP error from weather.gov: {e} | Response: {getattr(e.response, 'text', '')}")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
