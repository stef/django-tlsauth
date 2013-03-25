from django.conf.urls import patterns, url
from views import renderUserForm, renderCSRForm, renderCert, showcsrs, certify, reject, testAuth

urlpatterns = patterns('',
    # Examples:
    url(r'^register/$', renderUserForm),
    url(r'^certify/$', renderCSRForm),
    url(r'^cert/$', renderCert),
    url(r'^csrs/$', showcsrs),
    url(r'^sign/(?P<id>.+)$', certify),
    url(r'^reject/(?P<id>.+)$', reject),
    url(r'^test/$', testAuth),
)
