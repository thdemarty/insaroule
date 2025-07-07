import requests

from celery import shared_task
from django.conf import settings

"""
We wanted to use the adresse.data.gouv.fr API, but the service is migrating
to a new API at data.geopf.fr.
The documentation for the new API can be found here:
https://geoservices.ign.fr/documentation/services/services-geoplateforme/geocodage
"""

API_BASE_URL = "https://data.geopf.fr/geocodage/search"


@shared_task(rate_limit=settings.GEOCODAGE_TASK_RATE_LIMIT)
def get_autocompletion(query):
    """
    A Celery task to get latitude and longitude for a given query.
    This is a placeholder function that should be implemented with actual logic.

    API doc: https://geoservices.ign.fr/documentation/services/services-geoplateforme/autocompletion
    """

    r = requests.get(
        f"https://data.geopf.fr/geocodage/completion/?text={query}&terr=METROPOLE&type=StreetAddress",
        timeout=5,
    )
    result = []
    if r.status_code == 200:
        data = r.json()
        if data and "results" in data:
            geocoding_results = data["results"]
            if geocoding_results:
                for geocoding_result in geocoding_results:
                    result.append(
                        {
                            "fulltext": geocoding_result["fulltext"],
                            "value": f"{geocoding_result['y']}/{geocoding_result['x']}",
                            "customProperties": {
                                "street": geocoding_result.get("street", ""),
                                "city": geocoding_result.get("city", ""),
                                "zipcode": geocoding_result.get("zipcode", ""),
                                "latitude": geocoding_result["x"],
                                "longitude": geocoding_result["y"],
                            },
                        }
                    )
    return result


@shared_task(rate_limit=settings.ROUTING_TASK_RATE_LIMIT)
def get_routing(start, end):
    """
    A Celery task to get routing information.
    This is a placeholder function that should be implemented with actual logic.
    """
    r = requests.get(
        f"https://data.geopf.fr/navigation/itineraire?resource=bdtopo-osrm&start={start}&end={end}&profile=car&optimization=fastest&geometryFormat=geojson&getSteps=true&getBbox=true&distanceUnit=kilometer&timeUnit=hour&crs=EPSG%3A4326"
    )

    if r.status_code == 200:
        return r.json()
    else:
        return {
            "error": "Failed to fetch routing information",
            "status_code": r.status_code,
        }
