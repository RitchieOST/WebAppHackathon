# 10. Wasserkraft im Vergleich zu PV TEST
# mit pip freeze alle Libraries abrufen im Anschluss pip freeze > Libraries.txt  um alle Libraries unter File Libraries zu speichern
# pip install -r Libraries.txt	# um alle Libraries aus textfile zu installieren
#------------------------------------------------------------------------------------
#-----------------------------------------------------------------------




#------------------------------------------------------------------------------------

#Anzeige mit kumuliertem Verlauf in selbem Graph

import openmeteo_requests
import matplotlib.pyplot as plt
import pandas as pd
import requests_cache




def weatherdatagraph ():
    from retry_requests import retry_session

    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry_session(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 47.1415,
        "longitude": 9.5215,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "daily": "rain_sum",
        "hourly": ["temperature_2m", "shortwave_radiation"],
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # verarbeitung der stündlichen Daten
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_shortwave_radiation = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dataframe["shortwave_radiation_cumsum"] = hourly_dataframe["shortwave_radiation"].cumsum()

    # verarbeitung der täglichen Daten
    daily = response.Daily()
    daily_rain_sum = daily.Variables(0).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["rain_sum"] = daily_rain_sum
    daily_dataframe = pd.DataFrame(data = daily_data)
    daily_dataframe["rain_cumsum"] = daily_dataframe["rain_sum"].cumsum()



    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=False)

    # 1. Temperatur (stündlich)
    axes[0].plot(hourly_dataframe["date"], hourly_dataframe["temperature_2m"], color="tomato", linewidth=1)
    axes[0].set_ylabel("Temperatur (°C)")
    axes[0].set_title("Wetter Vaduz 2025")
    axes[0].grid(True, alpha=0.3)

    # 2. Strahlung + kumuliert (zweite Y-Achse)
    ax2_twin = axes[1].twinx()
    axes[1].fill_between(hourly_dataframe["date"], hourly_dataframe["shortwave_radiation"], color="gold", alpha=0.7, label="Strahlung")
    ax2_twin.plot(hourly_dataframe["date"], hourly_dataframe["shortwave_radiation_cumsum"], color="darkorange", linewidth=1.5, label="kumuliert")
    axes[1].set_ylabel("Strahlung (W/m²)")
    ax2_twin.set_ylabel("Strahlung kumuliert (W/m²)", color="darkorange")
    ax2_twin.tick_params(axis='y', labelcolor="darkorange")
    axes[1].grid(True, alpha=0.3)
    lines1, labels1 = axes[1].get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    axes[1].legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # 3. Regen + kumuliert (zweite Y-Achse)
    ax3_twin = axes[2].twinx()
    axes[2].bar(daily_dataframe["date"], daily_dataframe["rain_sum"], color="steelblue", width=0.6, label="Regen/Tag")
    ax3_twin.plot(daily_dataframe["date"], daily_dataframe["rain_cumsum"], color="navy", linewidth=1.5, label="kumuliert")
    axes[2].set_ylabel("Regen (mm/Tag)")
    ax3_twin.set_ylabel("Regen kumuliert (mm)", color="navy")
    ax3_twin.tick_params(axis='y', labelcolor="navy")
    axes[2].set_xlabel("Datum")
    axes[2].grid(True, alpha=0.3)
    lines1, labels1 = axes[2].get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    axes[2].legend(lines1 + lines2, labels1 + labels2, loc="upper left")




    plt.tight_layout()
    plt.savefig("Einzugsgebiet/static/figure.png")  # zuerst speichern
    plt.show()                                     # dann anzeigen