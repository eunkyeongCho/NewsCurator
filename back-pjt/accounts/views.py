from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'message': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'message': '이미 존재하는 사용자입니다.'}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_user(username=username, password=password)
    return Response({'message': '회원가입이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
