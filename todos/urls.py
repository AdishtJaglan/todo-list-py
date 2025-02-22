from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.loginUser, name="loginUser"),
    path("register/", views.registerUser, name="registerUser"),
    path("logout/", views.logoutUser, name="logoutUser"),
    path("create", views.createTodos, name="createTodos"),
    path("info", views.viewAll, name="viewAll"),
    path("info/<int:pk>", views.viewOne, name="viewOne"),
    path("update/<int:pk>", views.updateOne, name="updateOne"),
    path("delete/<int:pk>", views.deleteOne, name="deleteOne"),
    path("reset_password/", views.resetPassword, name="resetPassword"),
    path("change_password/", views.changePassword, name="changePassword"),
    path("user_detail/<int:pk>", views.viewUserDetail, name="viewUserDetail"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
