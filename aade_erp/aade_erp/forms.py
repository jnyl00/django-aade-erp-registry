from django import forms


class APICredentialsForm(forms.Form):
    token_username = forms.CharField(max_length=1024, required=True)
    token_password = forms.CharField(
        widget=forms.PasswordInput(render_value=True), 
        max_length=1024, required=True
    )


class ErpFetchForm(forms.Form):
    pass


class ErpFetchUploadsForm(forms.Form):
    date_from = forms.DateField(
        widget=forms.DateInput(format="%d%m%Y", attrs={"placeholder": "DDMMYYYY"}),
        required=False, input_formats=['%d%m%Y']
    )
    date_to = forms.DateField(
        widget=forms.DateInput(format="%d%m%Y", attrs={"placeholder": "DDMMYYYY"}),
        required=False, input_formats=['%d%m%Y']
    )


class ErpUploadForm(forms.Form):
    file = forms.FileField(required=True, widget=forms.FileInput(attrs={'accept':'text/csv'}))
