from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Todo
from .forms import TodoForm
from django.db.models import Case, When, Value, IntegerField
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST
import json
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.contrib import messages
from datetime import timedelta
from django.db.models import Count
from django.contrib.auth.decorators import login_required


@login_required
def todo_list(request):
    sort = request.GET.get('sort', '')
    todos = Todo.objects.filter(
        user=request.user,
        complete=False,
        is_deleted=False
    )
    
    if sort == 'importance':
        todos = todos.order_by('-important', 'created')
    elif sort == 'deadline':
        todos = todos.order_by('deadline', '-important')
    elif sort == 'created':
        todos = todos.order_by('created')
    else:
        todos = todos.order_by('order', 'created')
    
    return render(request, 'todo/todo_list.html', {'todos': todos})


@login_required
def todo_post(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'todo/todo_post.html', {'form': form})


@login_required
def done_list(request):
    todos = Todo.objects.filter(
        user=request.user,
        complete=True
    ).order_by('-completed_at')
    return render(request, 'todo/done_list.html', {'todos': todos})


@login_required
def todo_done(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.complete = not todo.complete
    todo.completed_at = timezone.now() if todo.complete else None
    todo.save()
    return redirect('todo_list')


@login_required
def todo_edit(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save()
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/todo_edit.html', {
        'form': form,
        'todo': todo  # todo 객체도 템플릿으로 전달
    })


@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.is_deleted = True
    todo.deleted_at = timezone.now()
    todo.save()
    return redirect('todo_list')


@login_required
def trash_list(request):
    todos = Todo.objects.filter(
        user=request.user,
        is_deleted=True
    ).order_by('-deleted_at')
    return render(request, 'todo/trash_list.html', {'todos': todos})


@login_required
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
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'계정이 생성되었습니다. {username}님 환영합니다!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'todo/user_add.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # 로그인 후 리다이렉트할 페이지
        else:
            # 로그인 실패 메시지 추가
            return render(request, 'login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})
    return render(request, 'login.html')


@login_required
def todo_stats(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=6)
    month_ago = today - timedelta(days=29)

    # 현재 사용자의 통계만 계산
    daily_completed = Todo.objects.filter(
        user=request.user,
        complete=True,
        completed_at__date=today
    ).count()

    weekly_completed = Todo.objects.filter(
        user=request.user,
        complete=True,
        completed_at__date__gte=week_ago,
        completed_at__date__lte=today
    ).count()

    monthly_completed = Todo.objects.filter(
        user=request.user,
        complete=True,
        completed_at__date__gte=month_ago,
        completed_at__date__lte=today
    ).count()

    total_completed = Todo.objects.filter(
        user=request.user,
        complete=True
    ).count()

    # 남은 퀘스트 정보
    remaining_quests = Todo.objects.filter(
        user=request.user,
        complete=False,
        is_deleted=False
    )
    remaining_total = remaining_quests.count()
    remaining_important = remaining_quests.filter(important__gte=4).count()
    remaining_today = remaining_quests.filter(deadline__date=today).count()

    # 레벨 계산
    def get_level_info(total_completed):
        levels = [
            (0, 10, 1, "견습 모험가"),
            (11, 25, 2, "열정적인 초보자"),
            (26, 50, 3, "꾸준한 실천가"),
            (51, 100, 4, "성실한 달성자"),
            (101, 200, 5, "숙련된 전문가"),
            (201, 350, 6, "대가의 길"),
            (351, 500, 7, "전설의 시작"),
            (501, 700, 8, "신화의 주인공"),
            (701, 1000, 9, "불멸의 영웅"),
            (1001, 1500, 10, "시간의 지배자"),
            (1501, 2000, 11, "운명의 조율사"),
            (2001, 3000, 12, "현실의 조각가"),
            (3001, 4000, 13, "차원의 여행자"),
            (4001, 5000, 14, "우주의 관리자"),
            (5001, float('inf'), 15, "무한의 창조자"),
        ]

        for min_count, max_count, level, title in levels:
            if min_count <= total_completed <= max_count:
                next_level = level + 1 if level < 15 else 15
                next_title = levels[level][3] if level < 15 else "무한의 창조자"
                progress = (total_completed - min_count) / (max_count - min_count) * 100
                remaining = max_count - total_completed
                return {
                    'level': level,
                    'title': title,
                    'next_level': next_level,
                    'next_title': next_title,
                    'progress': min(progress, 100),
                    'remaining': remaining
                }

    level_info = get_level_info(total_completed)

    context = {
        'daily_completed': daily_completed,
        'weekly_completed': weekly_completed,
        'monthly_completed': monthly_completed,
        'total_completed': total_completed,
        'remaining_total': remaining_total,
        'remaining_important': remaining_important,
        'remaining_today': remaining_today,
        'level_info': level_info,
    }

    return render(request, 'todo/todo_stats.html', context)