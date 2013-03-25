#!/usr/bin/env python

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from tlsauth import todn, gencert, mailsigned, load
import os, datetime
from forms import UserForm, CSRForm

def tlsauth(unauth=None, groups=None):
    """ decorator letting execution pass if TLS authenticated
        and if given certs Organization is in groups.

        if TLS authentication fails execution is diverted to unauth,
        which per default returns 403
    """
    if not unauth:
        def unauth(*args,**kwargs):
            return HttpResponse("Forbidden",status=403)
    def decor(func):
        def wrapped(request, *args,**kwargs):
            if request.META.get('verified')=="SUCCESS" and (not groups or todn(request.META.get('dn')).get('O') in groups):
                return func(request, *args,**kwargs)
            return unauth(request, *args,**kwargs)
        return wrapped
    return decor

def renderUserForm(request):
    """ form handles user registration requests.
        This is the web-based way to do this irresponsibly.
    """
    form = UserForm(request.POST)
    if form.is_valid():
        return HttpResponse(
            gencert(str(form.cleaned_data['name']),
                    str(form.cleaned_data['email']),
                    str(form.cleaned_data['org']),
                    settings.TLS_CA),
            mimetype="application/x-pkcs12")
    return render_to_response('register.html', {'form':form},context_instance=RequestContext(request) )

def renderCSRForm(request):
    """ form handles CSR submissions.
        blindsign disables reviewing by authorized personel, and enables automatic signing.
        scrutinizer is a function returning true if allowed to be signed.
    """
    form = CSRForm(request.POST)
    if not form.is_valid():
        return render_to_response('certify.html', {'form':form}, context_instance=RequestContext(request) )
    if settings.TLS_BLINDSIGN:
        if not settings.TLS_SCRUTINIZER or settings.TLS_SCRUTINIZER(str(form.cleaned_data['csr'])):
            return HttpResponse(settings.TLS_CA.signcsr(str(form.cleaned_data['csr'])),
                                mimetype="text/plain")
    settings.TLS_CA.submit(str(form.cleaned_data['csr']))
    return HttpResponse("Thank you. If all goes well you should soon "
                        "receive your signed certificate.")

def renderCert(request):
    """ provides the CA root cert
    """
    return HttpResponse(settings.TLS_CA._pub, mimetype="text/plain")

def certify(request, id):
    """ provides facility for users belonging to `groups` to sign incoming CSRs
    """
    err=authenticated(request, settings.TLS_ADMINGROUPS)
    if err: return err
    path=settings.TLS_CA._incoming+'/'+request.path.split('/')[3]
    print "certifying", path
    cert=settings.TLS_CA.signcsr(load(path))
    mailsigned([cert])
    os.unlink(path)
    return HttpResponseRedirect('/tlsauth/csrs/')

def reject(request, id):
    """ provides facility for users belonging to `groups` to reject incoming CSRs
    """
    err=authenticated(request, settings.TLS_ADMINGROUPS)
    if err: return err
    path=settings.TLS_CA._incoming+'/'+request.path.split('/')[3]
    os.unlink(path)
    return HttpResponseRedirect('/tlsauth/csrs/')

def authenticated(request, groups):
    """ helper function to check if user is authenticated and in a given group.
    """
    if not request.META.get('verified')=="SUCCESS" or (groups and todn(request.META.get('dn')).get('O') not in settings.TLS_ADMINGROUPS):
        return HttpResponse("Forbidden",status=403)

def showcsrs(request):
    """ authenticated view list of submitted CSRs
    """
    err=authenticated(request, settings.TLS_ADMINGROUPS)
    if err: return err
    return render_to_response('csrs.html',
                              {'certs': [(todn(cert.get_subject()),
                                      datetime.datetime.fromtimestamp(os.stat(path).st_mtime),
                                      os.path.basename(path))
                                     for cert, path
                                     in settings.TLS_CA.incoming()]})

def testAuth(request):
    """ test if you are TLS authenticated
        mountpoint: /tlsauth/test/
    """
    return HttpResponse(request.META.get('verified','') + "<br />" + request.META.get('dn',''))

