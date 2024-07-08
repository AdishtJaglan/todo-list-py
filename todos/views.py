from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

from .models import ToDoModel, User
from .forms import ToDoForm, UserLoginForm, UserRegistrationForm, PasswordChangeForm

User = get_user_model()


@login_required
def createTodos(request):
    form = ToDoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.user = request.user
        try:
            todo.save()
            messages.success(request, "To-do created successfully!")
            return redirect("viewAll")
        except ValidationError as e:
            messages.error(request, f"Error saving to-do: {e}")
    return render(request, "todos/createTodos.html", {"form": form})


@login_required
def viewAll(request):
    try:
        todos = ToDoModel.objects.filter(user=request.user)
    except ToDoModel.DoesNotExist:
        todos = None
        messages.error(request, "No to-dos found.")
    return render(request, "todos/viewTodos.html", {"dataset": todos})


@login_required
def viewOne(request, pk):
    try:
        todo = get_object_or_404(ToDoModel, id=pk, user=request.user)
    except ToDoModel.DoesNotExist:
        messages.error(request, "To-do not found.")
        return redirect("viewAll")
    return render(request, "todos/viewOne.html", {"data": todo})


@login_required
def updateOne(request, pk):
    try:
        todo = get_object_or_404(ToDoModel, id=pk, user=request.user)
    except ToDoModel.DoesNotExist:
        messages.error(request, "To-do not found.")
        return redirect("viewAll")

    form = ToDoForm(request.POST or None, request.FILES or None, instance=todo)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, "To-do updated successfully!")
            return redirect("viewOne", pk=todo.pk)
        except ValidationError as e:
            messages.error(request, f"Error updating to-do: {e}")
    return render(request, "todos/updateView.html", {"form": form})


@login_required
def deleteOne(request, pk):
    try:
        todo = get_object_or_404(ToDoModel, id=pk, user=request.user)
    except ToDoModel.DoesNotExist:
        messages.error(request, "To-do not found.")
        return redirect("viewAll")

    if request.method == "POST":
        try:
            todo.delete()
            messages.success(request, "To-do deleted successfully!")
            return redirect("viewAll")
        except ValidationError as e:
            messages.error(request, f"Error deleting to-do: {e}")
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
                messages.success(request, "Logged in successfully!")
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
            try:
                form.save()
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Registered and logged in successfully!")
                    return redirect("viewAll")
                else:
                    messages.error(request, "Registration failed. Please try again.")
            except ValidationError as e:
                messages.error(request, f"Error during registration: {e}")
    else:
        form = UserRegistrationForm()
    return render(request, "todos/register.html", {"form": form})


@login_required
def logoutUser(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("loginUser")


def resetPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        newPassword = request.POST.get("newPassword")
        try:
            user = User.objects.get(email=email)
            user.set_password(newPassword)
            user.save()
            messages.success(request, "Password reset successfully!")
            return redirect("loginUser")
        except User.DoesNotExist:
            messages.error(request, "User with the provided email does not exist.")
        except ValidationError as e:
            messages.error(request, f"Error resetting password: {e}")
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
                    messages.success(request, "Password updated successfully!")
                    return redirect("loginUser")
                else:
                    messages.error(request, "Old password is incorrect.")
            except User.DoesNotExist:
                messages.error(request, "User with the provided email does not exist.")
            except ValidationError as e:
                messages.error(request, f"Error updating password: {e}")
    else:
        form = PasswordChangeForm()
    return render(request, "todos/changePassword.html", {"form": form})


@login_required
def viewUserDetail(request, pk):
    try:
        user = get_object_or_404(User, id=pk)
    except User.DoesNotExist:
        messages.error(request, "User does not exist")
        return redirect("registerUser")
    return render(request, "todos/viewUserDetail.html", {"user": user})
