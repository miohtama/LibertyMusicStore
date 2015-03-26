from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class StoreSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        from .models import Store
        return Store.objects.all()

    # def lastmod(self, obj):
    #   return obj.pub_date

    def location(self, obj):
        """ """
        return "/store/{}/bitcoin/".format(obj.slug)


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)