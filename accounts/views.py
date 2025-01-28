from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from accounts.models import OneTimePassword
from accounts.serializers import PasswordResetRequestSerializer,LogoutUserSerializer, UserRegisterSerializer, LoginSerializer, SetNewPasswordSerializer, SetNewPasswordWithOtpSerializer, UserProfileSerializer
from rest_framework import status
from .utils import send_generated_otp_to_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from .models import User, UserProfile
from rest_framework.exceptions import NotFound
# Create your views here.


class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            print(user)
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            
            return Response({'message':'passcode is invalid, user is already verified.'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as indentifier:
            print(indentifier)
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        # return Response({'message':'user with that email does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    



class PasswordResetConfirm(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)
    
class SetNewPasswordWithOtpView(GenericAPIView):
    serializer_class=SetNewPasswordWithOtpSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)


class TestingAuthenticatedReq(GenericAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):

        data={
            'msg':'its works'
        }
        return Response(data, status=status.HTTP_200_OK)

class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
# Create your views here.

class UserProfileView(RetrieveUpdateAPIView): 
    serializer_class = UserProfileSerializer 
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        print(self.request.body) 
        return UserProfile.objects.get(user=self.request.user)
    

class TermsAndConditions(GenericAPIView):
    def get(self, request):
        return Response({'message':'terms and conditions'}, status=status.HTTP_200_OK)
    
class PrivacyPolicy(GenericAPIView):
    def get(self, request):
        privacy_policy = {
            "effective_date": "2025-01-27",
            "introduction": "Welcome to [App Name]! We value your privacy and are committed to protecting your personal information. This Privacy Policy explains how we collect, use, store, and protect your information when you use our cookery app.",
            "information_we_collect": {
                "email_address": "To communicate with you and provide account-related notifications.",
                "name": "To personalize your experience within the app.",
                "google_login_information": {
                    "name": "Name provided by Google",
                    "email": "Email provided by Google",
                    "profile_picture": "Profile picture provided by Google"
                }
            },
            "how_we_use_your_information": "The information we collect is used solely for the following purposes...",
            "data_storage_and_security": "We take your privacy seriously...",
            "information_sharing": "We do not share, sell, or disclose your personal information...",
            "your_rights": "You have the right to access, update, or delete your personal information...",
            "changes_to_privacy_policy": "We may update this Privacy Policy from time to time...",
            "contact_us": {
                "company_name": "CookVerse",
                "contact_email": "arsalannaziri0786@gmail.com",
                "contact_address": "1234 Old karimganj, Gaya, Bihar, India",}}
        return Response(privacy_policy, status=status.HTTP_200_OK)