from django.urls import include, path

from mytask import views

urlpatterns = [
    path('signup/', views.SignUp.as_view()),
    path('user/', views.AdminCreateUserApi.as_view()),
    path('update-user/<int:pk>/', views.SignUp.as_view()),
    path('login/', views.LoginApi.as_view()),
    path('task/', views.TaskApi.as_view()),
    path('task/<int:pk>/', views.TaskApi.as_view()),
    path('view-task/<int:pk>/', views.TaskViewApi.as_view()),
    path('view-tasks/', views.TasksView.as_view()),
    path('logout/', views.LogoutApi.as_view()),
    path('role/', views.RoleApi.as_view()),
    path('tasks/', views.TaskListView.as_view()),
]