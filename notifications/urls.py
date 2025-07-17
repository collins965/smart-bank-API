from django.urls import path
from .views import UserNotificationsView

urlpatterns = [
    path('user/notifications/', UserNotificationsView.as_view(), name='user-notifications'),
]
