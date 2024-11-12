from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Todo
from .forms import TodoForm


def todo_list(request):
    todos = Todo.objects.filter(complete=False)
    return render(request, 'todo/todo_list.html', {'todos': todos})


def todo_detail(request, pk):
    todo = Todo.objects.get(id=pk)
    return render(request, 'todo/todo_detail.html', {'todo': todo})


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
    dones = Todo.objects.filter(complete=True)
    return render(request, 'todo/done_list.html', {'dones': dones})


def todo_done(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.complete = True
    todo.save()
    return redirect('todo_list')


def todo_edit(request, pk):
    todo = Todo.objects.get(id=pk)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.save()
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/todo_post.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

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