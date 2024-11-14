from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Todo
from .forms import TodoForm, ProfileEditForm 
from .forms import TodoForm, ProfileEditForm 
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
from django.views.decorators.csrf import ensure_csrf_cookie

def calculate_level_and_title(completed_count):
    """
    완료된 퀘스트 수에 따라 레벨과 칭호를 계산하는 함수
    """
    if completed_count <= 10:
        return 1, "견습 모험가"
    elif completed_count <= 25:
        return 2, "열정적인 초보자"
    elif completed_count <= 50:
        return 3, "꾸준한 실천가"
    elif completed_count <= 100:
        return 4, "성실한 달성자"
    elif completed_count <= 200:
        return 5, "숙련된 전문가"
    elif completed_count <= 350:
        return 6, "대가의 길"
    elif completed_count <= 500:
        return 7, "전설의 시작"
    elif completed_count <= 700:
        return 8, "신화의 주인공"
    elif completed_count <= 1000:
        return 9, "불멸의 영웅"
    elif completed_count <= 1500:
        return 10, "시간의 지배자"
    elif completed_count <= 2000:
        return 11, "운명의 조율사"
    elif completed_count <= 3000:
        return 12, "현실의 조각가"
    elif completed_count <= 4000:
        return 13, "차원의 여행자"
    elif completed_count <= 5000:
        return 14, "우주의 관리자"
    else:
        return 15, "무한의 창조자"

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
    
    # 이전 레벨 가져오기 (세션에 저장된 값)
    previous_level = request.session.get('user_level', 0)
    
    # 현재 레벨 계산
    completed_todos = Todo.objects.filter(
        user=request.user,
        complete=True,
        is_deleted=False
    ).count()
    
    level, title = calculate_level_and_title(completed_todos)
    
    # 레벨업 확인
    is_level_up = level > previous_level
    
    # 현재 레벨을 세션에 저장
    request.session['user_level'] = level
    
    user_stats = {
        'level': level,
        'title': title,
        'completed_count': completed_todos,
        'is_level_up': is_level_up,  # 템플릿에 레벨업 여부 전달
    }
    
    return render(request, 'todo/todo_list.html', {
        'todos': todos,
        'sort': sort,
        'user_stats': user_stats,
    })


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
        complete=True,
        is_deleted=False
    ).order_by('-completed_at')
    return render(request, 'todo/done_list.html', {'todos': todos})


@login_required
def todo_done(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    
    # 이전 완료된 퀘스트 수와 레벨
    previous_completed = Todo.objects.filter(
        user=request.user,
        complete=True,
        is_deleted=False
    ).count()
    previous_level, _ = calculate_level_and_title(previous_completed)
    
    # 퀘스트 완료 처리
    todo.complete = True
    todo.completed_at = timezone.now()
    todo.save()
    
    # 새로운 레벨 계산
    new_completed = previous_completed + 1
    new_level, new_title = calculate_level_and_title(new_completed)
    
    # 레벨업 여부 확인
    is_level_up = new_level > previous_level
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_level_up': is_level_up,
            'new_level': new_level,
            'new_title': new_title,
            'completed_count': new_completed
        })
    
    return redirect('done_list')


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
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.is_deleted = False
    todo.deleted_at = None
    todo.save()
    
    return redirect('todo_list')


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


@ensure_csrf_cookie
@require_POST
def todo_delete_multiple(request):
    try:
        data = json.loads(request.body)
        todo_ids = data.get('ids', [])
        
        if not todo_ids:
            return JsonResponse({'status': 'error', 'message': '선택된 Quest가 없습니다.'}, status=400)
        
        # 선택된 todo 항목들 미수락 처리
        updated = Todo.objects.filter(
            id__in=todo_ids,
            user=request.user
        ).update(
            is_deleted=True,
            deleted_at=timezone.now()
        )
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


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

@login_required
def profile_view(request):
    return render(request, 'todo/profile.html', {'user': request.user})

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
        'character_image': user.character_image,  # character_image 프로퍼티 사용
    }
    return render(request, 'todo/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    
    character_images = {
        'char1': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEisDy2OZcb2ys4Hd7eCNf2PW5-VhcyOPiVGgG29ftptAUc0j7VmahVZ4Ne7lzj9Ty79at-SDWxKHGNHHrtRNx02pRnyRscF6ZDvm2oFqEOBQiIMUfM8n4lu7dqTF2c6gi48Zxz2EWa40KLXQTCQ2OvMaetQipNuccyujXIdtk97R-rq1tnrlt3pNVHMOxSs/s320/char1.jpg",
            'char2': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg8mO5R62gO068Y3jcc5nXgEJ5fTes4l2dNW9Gfiz-w9Sd5kh2u4LKj22-6P_quOVoXs3C3YoxpmmU1K8D3THHkawSGKTkx1EitF13Qy-86W2qA_s1_H3uzHnV4sR8khnLVsqlC7fGD7izXzPJutdRL3uWHzj75jUW4B52OIWfD2f6iKDKnmxkGM62BSQwM/s320/Char2.jpg",
            'char3': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjuBWeWD6ybcYqdmgB7X7g88c2zQ1OrAB8bFFi3LQolQyKaYKLVnr-zdLrf0V8c4m6-ePpOdEkLGlZieXyEliqnkG-wICfApL5RTjQLHWzQtYZqDur39U6_fy_xFKAVPuiAzPmTAZNLUiW5dk6c0EzpD6NKnYUiJV0pAcIZ1A-OVkwJJANen2rSV2qfdcJC/s320/Char3.jpg",
    }
    
    return render(request, 'todo/profile_edit.html', {
        'form': form,
        'character_images': character_images
    })

@require_POST
def todo_reorder(request):
    try:
        data = json.loads(request.body)
        todo_id = data.get('id')
        new_order = data.get('order')
        
        if todo_id is None or new_order is None:
            return JsonResponse({'status': 'error', 'message': '필수 데이터가 누락되었습니다.'}, status=400)
        
        # 해당 todo 항목 가져오기
        todo = Todo.objects.get(pk=todo_id, user=request.user)
        
        # 순서 업데이트
        todos = Todo.objects.filter(user=request.user, complete=False, is_deleted=False)
        if new_order < todo.order:  # 위로 이동
            todos.filter(order__gte=new_order, order__lt=todo.order).update(order=F('order') + 1)
        else:  # 아래로 이동
            todos.filter(order__gt=todo.order, order__lte=new_order).update(order=F('order') - 1)
        
        todo.order = new_order
        todo.save()
        
        return JsonResponse({'status': 'success'})
        
    except Todo.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '해당 Quest를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def todo_delete_permanent(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.delete()  # 실제로 데이터베이스에서 삭제
    return redirect('trash_list')

@login_required
def restore_incomplete(request, pk):
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    todo.complete = False
    todo.completed_at = None
    todo.save()
    return redirect('done_list')