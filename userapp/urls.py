from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='userapp-index'),
    path('index/', views.index, name='userapp-index'),
    path('registration/', views.registration, name='userapp-registration'),
    path('login/', views.login, name='userapp-login'),
    path('logout/', views.logout, name='userapp-logout'),
    path('register_building/',views.register_building, name='userapp-register-building'),
    path('notification/', views.notification, name='userapp-notification'),
    path('handshake/',views.handshake, name='userapp-handshake'),
    path('get_now_building/', views.show_current_info, name='userapp-get-user-current-information'),
    path('get_all_building/', views.show_all_info, name='userapp-get-user-all-information')
]