from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from django.views.generic.edit import FormView

import reports

class Report(View):
    template = 'reports/report.html'

    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user.username)
        if not user.is_staff:
            return HttpResponseRedirect(reverse('login'))

        name = kwargs.setdefault('name', None)
        if name is None:
            # list all the reports

        else:
            # display the requested report or 404
            
        return render(request, self.template)
