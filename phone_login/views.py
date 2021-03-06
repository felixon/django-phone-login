import json

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import status

from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate, logout

from phone_login.models import PhoneToken

from phone_login.utils import (failure, success,
        unauthorized, too_many_requests, user_detail)


from .serializers import PhoneTokenCreateSerializer, PhoneTokenValidateSerializer

class GenerateOTP(CreateAPIView):

    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenCreateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(data=request.data, context={'request': request})
        if ser.is_valid():
            token = PhoneToken.create_otp_for_number(request.data.get('phone_number'))
            phone_token = self.serializer_class(token, context={'request': request})
            return Response(phone_token.data)
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ValidateOTP(CreateAPIView):

    queryset = PhoneToken.objects.all()
    serializer_class = PhoneTokenValidateSerializer

    def post(self, request, format=None):
        # Get the patient if present or result None.
        ser = self.serializer_class(data=request.data, context={'request': request})
        if ser.is_valid():

            pk = request.data.get("pk")
            otp = request.data.get("otp")
            try:
                user = authenticate(pk=pk, otp=otp)
                last_login = user.last_login
                login(request, user)
                response = user_detail(user, last_login)
                return Response(response, status = status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response(
                {'reason': "OTP doesn't exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(
            {'reason': ser.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
