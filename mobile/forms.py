from django import forms

from django.core.cache import caches


class CredentialForm(forms.Form):

    username = forms.CharField(
        label='用户名', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def set_cache(self):
        cache = caches['default']
        cache.set('sps_username', self.data['username'], 360)
        cache.set('sps_password', self.data['password'], 360)
