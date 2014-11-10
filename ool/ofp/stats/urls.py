from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from ool.ofp.stats.service.endpoint import set_desc_stats, set_port_stats, set_port_desc_stats, set_flow_stats
from ool.ofp.stats.service.endpoint import datapathid_list, desc, stats_req, stats_req_start, stats_req_stop

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ool.ofp.stats.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^ofpm/stats/set_desc_stats$', set_desc_stats),
	url(r'^ofpm/stats/set_port_stats$', set_port_stats),
	url(r'^ofpm/stats/set_port_desc_stats$', set_port_desc_stats),
	url(r'^ofpm/stats/set_flow_stats$', set_flow_stats),
	url(r'^ofpm/stats/datapathid_list$', datapathid_list),
	url(r'^ofpm/stats/desc$', desc),
	url(r'^ofpm/stats/desc/(?P<dpid>\w+)$', desc),
	url(r'^ofpm/stats/stats_req$', stats_req),
	url(r'^ofpm/stats/stats_req_start$', stats_req_start),
	url(r'^ofpm/stats/stats_req_stop$', stats_req_stop),
)
