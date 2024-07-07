from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import ToDoModel, User
from .forms import ToDoForm, UserLoginForm, UserRegistrationForm, PasswordChangeForm

User = get_user_model()


@login_required
def createTodos(request):
    form = ToDoForm(request.POST or None)

    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        todo.save()
        return redirect("viewAll")

    return render(request, "todos/createTodos.html", {"form": form})


@login_required
def viewAll(request):
    todos = ToDoModel.objects.filter(user=request.user)
    return render(request, "todos/viewTodos.html", {"dataset": todos})


@login_required
def viewOne(request, pk):
    todo = get_object_or_404(ToDoModel, id=pk, user=request.user)
    return render(request, "todos/viewOne.html", {"data": todo})


@login_required
def updateOne(request, pk):
    todo = get_object_or_404(ToDoModel, id=pk, user=request.user)
    form = ToDoForm(request.POST or None, instance=todo)

    if form.is_valid():
        form.save()
        return redirect("viewOne", pk=todo.pk)

    return render(request, "todos/updateView.html", {"form": form})


@login_required
def deleteOne(request, pk):
    todo = get_object_or_404(ToDoModel, id=pk, user=request.user)

    if request.method == "POST":
        todo.delete()
        return redirect("viewAll")

    return render(request, "todos/deleteTodo.html", {"todo": todo})


def loginUser(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("viewAll")
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = UserLoginForm()
    return render(request, "todos/login.html", {"form": form})


def registerUser(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("viewAll")
            else:
                messages.error(request, "Registration failed. Please try again.")
    else:
        form = UserRegistrationForm()
    return render(request, "todos/register.html", {"form": form})


@login_required
def logoutUser(request):
    logout(request)
    return redirect("loginUser")


def resetPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        newPassword = request.POST.get("newPassword")

        try:
            user = User.objects.get(email=email)
            user.set_password(newPassword)
            user.save()
            return redirect("loginUser")
        except User.DoesNotExist:
            messages.error(request, "User with the provided email does not exist")

    return render(request, "todos/resetPassword.html")


def changePassword(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            old_password = form.cleaned_data.get("old_password")
            new_password = form.cleaned_data.get("new_password")

            try:
                user = User.objects.get(email=email)
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Password updated successfully.")
                    return redirect("loginUser")
                else:
                    messages.error(request, "Old password is incorrect.")
            except User.DoesNotExist:
                messages.error(request, "User with the provided email does not exist.")
    else:
        form = PasswordChangeForm()
    return render(request, "todos/changePassword.html", {"form": form})
