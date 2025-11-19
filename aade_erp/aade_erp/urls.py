"""
URL configuration for aade_erp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from .views import (
    HomeView, 
    APICredentialsView, 
    ErpFetchView, 
    ErpFetchUploadsView, 
    ErpUploadView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Local
    path('', login_required(HomeView.as_view()), name='home'), 
    path('api-credentials/', APICredentialsView.as_view(), name='api_credentials'), 
    path('erp/fetch/priority/afm/', ErpFetchView.as_view(), name='fetch_priority'), 
    path('erp/fetch/upload/info/<int:trans_id>/', ErpFetchView.as_view(), name='fetch_upload_info'), 
    path('erp/fetch/upload/csv/<int:trans_id>/', ErpFetchView.as_view(), name='fetch_upload_file'), 
    path('erp/fetch/uploads/', ErpFetchUploadsView.as_view(), name='fetch_uploads'), 
    
    path('erp/upload/erpReady/submit/', ErpUploadView.as_view(), name='upload_erpready_submit'), 
    path('erp/upload/erpReady/validate/', ErpUploadView.as_view(), name='upload_erpready_validate'), 
    path('erp/upload/submit/', ErpUploadView.as_view(), name='upload_erp_submit'), 
    path('erp/upload/validate/', ErpUploadView.as_view(), name='upload_erp_validate'), 
    path('erp/upload/erpInstaller/submit/', ErpUploadView.as_view(), name='upload_erpinstaller_submit'), 
    path('erp/upload/erpInstaller/validate/', ErpUploadView.as_view(), name='upload_erpinstaller_validate'), 
]
