from django.urls import path
from . import views

app_name = 'authy'

urlpatterns = [
    path('',views.Login,name='login'),
    path('register/',views.Signup, name='signup')
]