import requests
import simplejson as json

from django.conf import settings
from django.views.generic import TemplateView
from requests_ntlm import HttpNtlmAuth


class IndexView(TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sps_username = 'corp\\administrator'
        sps_password = ''
        sps_site_url = settings.SPS_ROOT + '/sites/it/_api/web/lists'
        sps_headers = {'accept': 'application/json'}

        response = requests.get(sps_site_url, auth=HttpNtlmAuth(
            sps_username, sps_password), headers=sps_headers)

        json_data = json.loads(response.content)

        context['sps_lists'] = [x['Title'] for x in json_data['value']]

        return context
