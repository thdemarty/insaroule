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
def get_lat_lng(query, limit=5):
    """
    A Celery task to get latitude and longitude for a given query.
    This is a placeholder function that should be implemented with actual logic.
    """
    return None
