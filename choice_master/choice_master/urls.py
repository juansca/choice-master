"""choice_master URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from allauth.account import views

urlpatterns = [
    url(r'^', include('chm.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^signup/$', views.signup, name="account_signup"),
    url(r'^login/$', views.login, name="account_login"),
    url(r'^logout/$', views.logout, name="account_logout"),

    # Uncomment this in case we need to support password change
    # url(r"^password/change/$", views.password_change,
    #     name="account_change_password"),
    # url(r"^password/set/$", views.password_set, name="account_set_password"),
]
