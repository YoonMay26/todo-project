from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.todo_list, name='todo_list'),
    path('post/', views.todo_post, name='todo_post'),
    path('edit/<int:pk>/', views.todo_edit, name='todo_edit'),
    path('done/<int:pk>/', views.todo_done, name='todo_done'),
    path('done/', views.done_list, name='done_list'),
    path('delete/<int:pk>/', views.todo_delete, name='todo_delete'),
    path('stats/', views.todo_stats, name='todo_stats'),
    path('trash/', views.trash_list, name='trash_list'),
    path('restore/<int:pk>/', views.todo_restore, name='todo_restore'),
    path('reorder/', views.reorder_todos, name='reorder_todos'),
    path('todo/delete-multiple/', views.todo_delete_multiple, name='todo_delete_multiple'),
    path('detail/<int:pk>/', views.todo_detail_json, name='todo_detail_json'),
    path('user_add/', views.user_add, name='user_add'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('login/', auth_views.LoginView.as_view(
    template_name='todo/login.html',
    redirect_authenticated_user=True,
    extra_context={'show_register_link': True}
        ), name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('todo/restore/<int:pk>/', views.todo_restore, name='todo_restore'),
    path('todo/delete-permanent/<int:pk>/', views.todo_delete_permanent, name='todo_delete_permanent'),
    path('todo/delete-multiple/', views.todo_delete_multiple, name='todo_delete_multiple'),
    path('todo/restore-incomplete/<int:pk>/', views.restore_incomplete, name='restore_incomplete'),
]