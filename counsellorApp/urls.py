from django.urls import path
from . import views

urlpatterns=[
    path('', views.loginPage, name='login'),
    path('home', views.home, name='home'),
    path('cdc', views.cdc, name='cdc'),
    path('signup', views.registerPage , name ="signup"),
    path('logout', views.logoutUser , name ="logout"),
    path('user', views.DataAdder, name='user'),
    path('viewer', views.DataFilter, name='filter'),
    path('date', views.filter, name='date'),
    path('adm',views.DataAdm, name='adm'), 
    path('batch',views.batch_detail_view, name='batch'),
      
    
]
