import json as jsonlib
from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView

import httpx

from .forms import (
    APICredentialsForm, 
    ErpFetchForm, ErpFetchUploadsForm, 
    ErpUploadForm
)
from .utils import BearerAuth


BASE_API_URL = "https://www1.aade.gr/aadeapps3/erpApi/rest/"


API_ENDPOINTS = {
    "fetch_priority": "erp/fetch/priority/afm/",
    "fetch_upload_info": "erp/fetch/upload/info/{trans_id}/",
    "fetch_upload_file": "erp/fetch/upload/csv/{trans_id}/",
    "fetch_uploads": "erp/fetch/uploads/",

    "upload_erpready_submit": "erp/upload/erpReady/submit/",
    "upload_erpready_validate": "erp/upload/erpReady/validate/",
    "upload_erp_submit": "erp/upload/submit/",
    "upload_erp_validate": "erp/upload/validate/",
    "upload_erpinstaller_submit": "erp/upload/erpInstaller/submit/",
    "upload_erpinstaller_validate": "erp/upload/erpInstaller/validate/",
}


API_ENDPOINT_TITLES = {
    "api_credentials": "Credentials",

    "fetch_priority": "Fetch Priority AFM",
    "fetch_upload_info": "Fetch Upload Info",
    "fetch_upload_file": "Fetch Upload File",
    "fetch_uploads": "Fetch Uploads",

    "upload_erpready_submit": "Upload Software Readiness File",
    "upload_erpready_validate": "Validate Software Readiness File",
    "upload_erp_submit": "Upload ERP File",
    "upload_erp_validate": "Validate ERP File",
    "upload_erpinstaller_submit": "Upload Associated Installers\' tin File",
    "upload_erpinstaller_validate": "Validate Associated Installers\' tin File",
}


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_api_credentials"] = bool("api_credentials" in self.request.session)
        return context


class BaseFormComponentView(FormView):
    template_name = "base_form.html"
    component_template_name = "components/base_form_component.html"

    def get_template_names(self):
        if self.request.htmx:
            if self.component_template_name is None:
                raise ImproperlyConfigured(
                    "TemplateResponseMixin requires either a definition of "
                    "'template_name' or an implementation of 'get_template_names()'"
                )
            else:
                return [self.component_template_name]
        else:
            return super().get_template_names()
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_endpoint_title = API_ENDPOINT_TITLES.get(self.request.resolver_match.view_name, "")
        if api_endpoint_title:
            context["component_title"] = api_endpoint_title
        return context
    

    def form_valid(self, form, response=None):
        """If the form is valid, render the clean form."""
        return self.render_to_response(
            self.get_context_data(component_response=response, component_response_str=f"{response}")
        )


class APICredentialsView(BaseFormComponentView):
    form_class = APICredentialsForm

    def get_initial(self):
        """
        Set form initials to already saved API credentials.
        """
        initials = super().get_initial()

        stashed_credentials = self.request.session.get('api_credentials', {})
        initials.update(stashed_credentials)

        return initials
    
    def form_valid(self, form):
        self.request.session['api_credentials'] = form.cleaned_data
        return super().form_valid(form, "Successfully saved the API credentials in temporary storage")


class ErpFetchView(BaseFormComponentView):
    form_class = ErpFetchForm

    def form_valid(self, form):
        api_endpoint = API_ENDPOINTS.get(self.request.resolver_match.view_name, "")
        api_url = f"{BASE_API_URL}{api_endpoint}".format(trans_id=self.kwargs.get('trans_id'))

        api_credentials = self.request.session.get('api_credentials', {})
        if api_credentials:
            auth = BearerAuth(**api_credentials)

            response = httpx.get(api_url, headers={"accept": "application/json"}, params=form.cleaned_data, auth=auth)

            # Workaround for htmx not being able to respect content download headers
            # https://github.com/bigskysoftware/htmx/issues/474
            if "content-disposition" in response.headers:
                rsp = HttpResponse(headers={"HX-Redirect": api_url})
                return rsp
            else:
                try:
                    response = {"status": response.status_code, "message": response.reason_phrase, "data": response.json()}
                except jsonlib.decoder.JSONDecodeError:
                    response = {"status": response.status_code, "message": response.reason_phrase}
        else:
            response = {'status': 400, "message": "No API credentials found"}

        return super().form_valid(form, response)


class ErpFetchUploadsView(ErpFetchView):
    form_class = ErpFetchUploadsForm


class ErpUploadView(BaseFormComponentView):
    form_class = ErpUploadForm

    def form_valid(self, form):
        api_endpoint = API_ENDPOINTS.get(self.request.resolver_match.view_name, "")
        api_url = f"{BASE_API_URL}{api_endpoint}"

        api_credentials = self.request.session.get('api_credentials', {})
        if api_credentials:
            auth = BearerAuth(**api_credentials)

            data = {}
            files = {}
            
            dj_file = form.cleaned_data.get('file', None)
            if dj_file:
                files["file"] = dj_file

            response = httpx.post(api_url, headers={"accept": "application/json"}, data=data, files=files, auth=auth)
            try:
                response = {"status": response.status_code, "message": response.reason_phrase, "data": response.json()}
            except jsonlib.decoder.JSONDecodeError:
                response = {"status": response.status_code, "message": response.reason_phrase}
        else:
            response = {'status': 400, "message": "No API credentials found"}

        return super().form_valid(form, response)
