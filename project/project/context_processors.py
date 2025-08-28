from django.conf import settings


def constants(request):
    return {
        "SUPPORT_EMAIL": settings.SUPPORT_EMAIL,
    }
