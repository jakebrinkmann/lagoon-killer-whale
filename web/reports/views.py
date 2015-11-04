from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.edit import FormView
from django.http import Http404
from django.template import loader

import reports

class Report(View):
    report_template = 'reports/report.html'
    listing_template = 'reports/list.html'
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        if not user.is_staff:
            return HttpResponseRedirect(reverse('login'))

        name = kwargs.setdefault('name', None)

        if name is None:
            results = reports.listing()
            t = loader.get_template(self.listing_template)
            html = t.render({'reports': results})
        else:
            # display the requested report or 404
            try:
                results = reports.run()
                t = loader.get_template(self.template)
                html = t.render({'report': results}, request)
            except NotImplementedError:
                raise Http404("Report {0} not found".format(name))
            
        return HttpResponse(html)
            
        
