from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('todo/', include('todo.urls')),
    path('', auth_views.LoginView.as_view(template_name='todo/login.html', extra_context={'show_register_link': True}), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
