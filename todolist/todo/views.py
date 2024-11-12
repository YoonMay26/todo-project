from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Todo
from .forms import TodoForm
from django.db.models import Case, When, Value, IntegerField
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
import json
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.urls import reverse


def todo_list(request):
    sort = request.GET.get('sort', '')
    todos = Todo.objects.filter(complete=False, is_deleted=False)
    
    if sort == 'importance':
        todos = todos.order_by('-important', 'created')
    elif sort == 'deadline':
        todos = todos.order_by(
            Case(
                When(deadline__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            'deadline',
            '-important'
        )
    elif sort == 'created':
        todos = todos.order_by('created')
    else:
        todos = todos.order_by('order', 'created')
    
    return render(request, 'todo/todo_list.html', {'todos': todos})


def todo_post(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.created = timezone.now()
            todo.save()
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'todo/todo_post.html', {'form': form})


def done_list(request):
    dones = Todo.objects.filter(complete=True, is_deleted=False)
    return render(request, 'todo/done_list.html', {'dones': dones})


def todo_done(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.complete = not todo.complete
    todo.completed_at = timezone.now() if todo.complete else None
    todo.save()
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    return HttpResponseRedirect(reverse('todo_list'))


def todo_edit(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save()
            return redirect('todo_list')
    else:
        # 기존 데이터로 폼을 초기화
        form = TodoForm(instance=todo)
        # datetime-local 입력을 위한 형식 변환
        if todo.deadline:
            form.initial['deadline'] = todo.deadline.strftime('%Y-%m-%dT%H:%M')
    
    return render(request, 'todo/todo_edit.html', {
        'form': form,
        'todo': todo
    })


# 삭제 뷰 새로 추가
def todo_delete(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.is_deleted = True
    todo.deleted_at = timezone.now()
    todo.save()
    return redirect('todo_list')


def trash_list(request):
    # is_deleted가 True인 항목만 가져오기
    todos = Todo.objects.filter(is_deleted=True).order_by('-deleted_at')
    return render(request, 'todo/trash_list.html', {'todos': todos})


def todo_restore(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.is_deleted = False
    todo.deleted_at = None
    todo.save()
    return redirect('trash_list')


@require_POST
def reorder_todos(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        # 각 항목의 순서 업데이트
        for index, item_id in enumerate(items):
            Todo.objects.filter(id=item_id).update(order=index)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
def bulk_delete(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        Todo.objects.filter(id__in=items).update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def todo_detail_json(request, pk):
    todo = Todo.objects.get(id=pk)
    data = {
        'title': todo.title,
        'description': todo.description,
        'created': todo.created.strftime('%Y-%m-%d %H:%M'),
        'completed_at': todo.completed_at.strftime('%Y-%m-%d %H:%M') if todo.completed_at else None,
        'deadline': todo.deadline.strftime('%Y-%m-%d %H:%M') if todo.deadline else None,
        'important': todo.important,
    }
    return JsonResponse(data)



def user_add(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('todo_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'todo/user_add.html', {'form': form})
