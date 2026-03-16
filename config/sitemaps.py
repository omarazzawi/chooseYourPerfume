from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'history', 'consultations:consultation_list']

    def location(self, item):
        return reverse(item)