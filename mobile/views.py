import logging

import requests
import simplejson as json
from django.conf import settings
from django.core.cache import caches
from django.http.response import HttpResponsePermanentRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from exchangelib import Account, Credentials, Configuration
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
from requests_ntlm import HttpNtlmAuth

from mobile.forms import CredentialForm

logger = logging.getLogger(__name__)


class IndexView(TemplateView):

    template_name = 'index.html'
    cache = caches['default']

    def dispatch(self, request, *args, **kwargs):
        if not self.request.session.has_key('username'):
            return HttpResponsePermanentRedirect('/login')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # get username from cache
        username = self.request.session['username']
        password = self.cache.get(username)

        # Tell exchangelib to use this adapter class instead of the default
        BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

        credentials = Credentials(username, password)
        config = Configuration(server='ex01.corp.contoso.com', credentials=credentials)
        account = Account(username, credentials=credentials, config=config)

        latest_messages = account.inbox.all().order_by('-datetime_received')[:100]
        context['messages'] = [{'subject': x.subject, 'sender': x.sender.email_address} for x in latest_messages]

        try:
            # retrieve data from sharepoint
            sps_site_url = settings.SPS_ROOT + \
                '/sites/it/_api/web/lists/GetByTitle(\'文档\')/Files'
            sps_headers = {'accept': 'application/json'}
            sps_username = 'corp\\{0}'.format(username.split('@')[0])
            response = requests.get(sps_site_url, auth=HttpNtlmAuth(
                sps_username, password), headers=sps_headers)
            json_data = json.loads(response.content)

            context['username'] = username
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
        self.request.session['username'] = form.data['username']
        return super().form_valid(form)


class LogoffView(TemplateView):

    template_name = 'logoff.html'
    cache = caches['default']

    def dispatch(self, request, *args, **kwargs):
        # delete existing username from session
        try:
            del self.request.session['username']
        except:
            pass
        return super().dispatch(request, *args, **kwargs)
