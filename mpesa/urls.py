from django.urls import path
from .views import STKPushView, STKCallbackView

urlpatterns = [
    path("stk-push/", STKPushView.as_view(), name="stk-push"),
    path("stk-push/callback/", STKCallbackView.as_view(), name="stk-callback"),
]
