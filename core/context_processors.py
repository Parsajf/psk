from .models import SiteSettings


def site_settings(request):
    return {'site_contact': SiteSettings.objects.first() or SiteSettings()}
