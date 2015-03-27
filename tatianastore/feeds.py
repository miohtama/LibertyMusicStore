from django.core.urlresolvers import reverse_lazy
from andablog.feeds import LatestEntriesFeed


class LatestBlogEntries(LatestEntriesFeed):
    feed_copyright = 'Liberty Music Store'
    title = 'Liberty Music Store latest Bitcoin music news'
    description = 'Updates on the libertymusicstore.net'
    link = reverse_lazy('andablog:entrylist')