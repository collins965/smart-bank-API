from django.urls import path
from .views import STKPushView

urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk-push"),
]
