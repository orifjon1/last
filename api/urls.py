from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from users import views
from task import views as View
from .views import TaskCancelView, TaskFinishView, ManagerToWorkerView
from .currency import Currency


urlpatterns = [
    # token refresh
    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),

    # logout
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # users
    path('signup/', views.UserSignUpView.as_view(), name='signup'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('user/stat/', views.UserStatView.as_view(), name='user_stat'),
    path('user/sector/<int:id>/', View.UserSectorView.as_view(), name='user_sector'),
    path('user/cabinet/<int:id>/', View.OneUserView.as_view(), name='user_cabinet'),
    path('user_cabinet/task/<int:id>/', View.OneUserTaskView.as_view(), name='user_cabinet_task'),

    # sector
    path('sector/', views.SectorView.as_view(), name='sector_list_create'),
    path('sector/stat/', View.SectorStatView.as_view(), name='sector_stat'),

    # tasks
    path('task/create/', View.TaskListCreateView.as_view(), name='task_list_create'),
    path('task/detail/', View.TaskDetailUpdateDeleteView.as_view(), name='detail_update_delete'),
    path('task/stat/', View.TaskStatView.as_view(), name='task_stat'),
    path('task/sector/<int:id>/', View.TaskSectorView.as_view(), name='sector_tasks'),
    path('task/sector/stat/<int:id>/', View.TaskSectorStatView.as_view(), name='task_sector_stat'),

    # review
    path('review/list/create/<int:id>/', View.ReviewView.as_view(), name='review_list_create'),
    path('review/edit/update/delete/<int:id>/', View.ReviewEditDelete.as_view(), name='review_edit_patch_delete'),

    # cancel task
    path('cancel/task/<int:id>/', TaskCancelView.as_view(), name='cancel_task'),

    # finish task
    path('finish/task/<int:id>/', TaskFinishView.as_view(), name='finish_task'),

    # send a task archive
    path('active/archive/<int:id>/', View.TaskIsActiveOrNotView.as_view(), name='Active_Archive'),

    # manager gives task to worker
    path('manager/<int:id>/<str:pk>/', ManagerToWorkerView.as_view(), name='manager_to_worker'),

    # currency exchange
    path('currency/', Currency.as_view(), name='currency'),

]
