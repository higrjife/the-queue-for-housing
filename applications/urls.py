from django.urls import path
from . import views


app_name = 'applications'

urlpatterns = [
    path('', views.home, name='home'),
    path('check-queue/', views.check_queue_number, name='check-queue'),
    path('list-queue/', views.queue_members, name='queue_members'),
    path('my-application/list/', views.my_applications, name='my-applications-list'),
    path('my-application/create', views.create_application, name="create-application"),
    path('my-application/<int:application_id>/', views.view_application, name='view-application'),
    path('my-application/edit/<int:application_id>/', views.edit_application, name='edit-application'),
    path('application/reject/<int:application_id>/', views.reject_application, name='reject-application'),
    # path('my-application/<int:application_id>/edit/', views.edit_application, name='edit-application'),
    path('application/update-status/<int:application_id>/<str:new_status>', views.update_application_status, name='update-application-status'),
    
    ## api
    # path('api/check-queue/', views.QueueCheckAPIView.as_view(), name='api_check_queue'),    
]