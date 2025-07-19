from django.core.mail import EmailMessage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings

class ContactView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        message = request.data.get('message')

        if not all([name, email, message]):
            return Response(
                {"error": "All fields (name, email, message) are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subject = f"SmartBank360 Contact Form - Message from {name}"
        body = (
            f"Sender Name: {name}\n"
            f"Sender Email: {email}\n\n"
            f"Message:\n{message}"
        )

        try:
            email_message = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.EMAIL_HOST_USER,  # Must match authenticated email
                to=[settings.EMAIL_HOST_USER],
                reply_to=[email],
            )
            email_message.send(fail_silently=False)
            return Response(
                {"success": "Message sent successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send message. Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
