from django import forms

class UserForm(forms.Form):
    """ (FLASK) simple registration WTForm
    """
    name = forms.CharField()
    email = forms.CharField()
    org = forms.CharField()

class CSRForm(forms.Form):
    """ (FLASK) even simpler CSR submission WTForm
    """
    csr = forms.CharField(widget=forms.Textarea)

