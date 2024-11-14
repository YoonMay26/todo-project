from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from todo import views as todo_views


urlpatterns = [
    path('', todo_views.index, name='index'),
    path('admin/', admin.site.urls),
    path('todo/', include('todo.urls')),
    path('login/', auth_views.LoginView.as_view(
        template_name='todo/login.html',
        extra_context={'show_register_link': True},
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('user_add/', todo_views.user_add, name='user_add'),
]