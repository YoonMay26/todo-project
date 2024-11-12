from django.urls import path
from . import views

urlpatterns = [
    path('', views.todo_list, name='todo_list'),
    path('post/', views.todo_post, name='todo_post'),
    path('edit/<int:pk>/', views.todo_edit, name='todo_edit'),
    path('done/', views.done_list, name='done_list'),
    path('done/<int:pk>/', views.todo_done, name='todo_done'),
    path('delete/<int:pk>/', views.todo_delete, name='todo_delete'),
    path('trash/', views.trash_list, name='trash_list'),
    path('restore/<int:pk>/', views.todo_restore, name='todo_restore'),
    path('reorder/', views.reorder_todos, name='reorder_todos'),
    path('bulk-delete/', views.bulk_delete, name='bulk_delete'),
    path('detail/<int:pk>/', views.todo_detail_json, name='todo_detail_json'),
]

