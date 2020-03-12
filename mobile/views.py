import logging

import requests
import simplejson as json

from django.conf import settings
from django.http.response import HttpResponsePermanentRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.core.cache import caches
from requests_ntlm import HttpNtlmAuth

from mobile.forms import CredentialForm

logger = logging.getLogger(__name__)

class IndexView(TemplateView):

    template_name = 'index.html'
    cache = caches['default']
    sps_username = None
    sps_password = None

    def dispatch(self, request, *args, **kwargs):
        # get username from cache
        self.sps_username = self.cache.get('sps_username')
        self.sps_password = self.cache.get('sps_password')

        if self.sps_username is None or self.sps_password is None:
            return HttpResponsePermanentRedirect('/login')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # retrieve data from sharepoint
            sps_site_url = settings.SPS_ROOT + \
                '/sites/it/_api/web/lists/GetByTitle(\'文档\')/Files'
            sps_headers = {'accept': 'application/json'}
            response = requests.get(sps_site_url, auth=HttpNtlmAuth(
                self.sps_username, self.sps_password), headers=sps_headers)
            json_data = json.loads(response.content)

            context['sps_username'] = self.sps_username
            context['sps_lists'] = [
                '{0}|{1}'.format(x['odata.type'], x['Name']) for x in json_data['value']]
        except Exception as ex:
            logger.error(str(ex))

        return context


class LoginView(FormView):
    template_name = 'login.html'
    form_class = CredentialForm
    success_url = '/'

    def form_valid(self, form):
        form.set_cache()
        return super().form_valid(form)


class LogoffView(TemplateView):

    template_name = 'logoff.html'
    cache = caches['default']

    def dispatch(self, request, *args, **kwargs):
        # delete username and password from cache
        self.cache.delete_many(['sps_username', 'sps_password'])
        return super().dispatch(request, *args, **kwargs)
