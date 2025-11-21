"""
URL configuration for prjFoodtrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from appFoodtrack import views

urlpatterns = [
    path('', views.inicio, name="menuInicial"),
    path('iniciarSesion/',views.inicioSesion, name="inicioSesion"),
    path('crearUsuario/',views.crearUsuario, name="crearUsuario"),
    path('logout/', views.logout, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('donacion/nueva/', views.crear_donacion, name="crearDonacion"),
    path('donacion/', views.ver_donaciones, name="verDonaciones"),
    path('donacion/editar/<int:donacion_id>/', views.editar_donacion, name="editar_donacion"),
    path('donacion/cancelar/<int:donacion_id>/', views.cancelar_donacion, name="cancelar_donacion"),
    path('donaciones/disponibles/', views.ver_donaciones_disponibles, name="ver_donaciones_disponibles"),
    path('donacion/aceptar/<int:donacion_id>/', views.aceptar_donacion, name="aceptar_donacion"),
    path('usuario/',views.usuario_list),
    path('usuario/<int:pk>',views.usuario_detail),
    path('donacion/seguimiento/<int:donacion_id>/', views.ver_seguimiento, name="ver_seguimiento"),
]
