from django.core import exceptions
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_409_CONFLICT, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.serializers import *


class Signup(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            voter = serializer.save()
            # jwt token
            token = TokenObtainPairSerializer.get_token(voter)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "username": voter.username,
                    "email": voter.email,
                    "message": "success!",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Vote(APIView):
    def get(self, request):  # vote 현황 가져오기
        candidates = Candidate.objects.all().order_by('-vote_cnt')
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)

    def post(self, request):
        candidate_name = self.request.data['candidate']
        candidate = Candidate.objects.get(candidate_name=candidate_name)

        voter_name = self.request.data['voter']
        voter = Voter.objects.get(username=voter_name)

        if not voter.voter_state:  # 아직 투표하지 않은 투표자라면
            candidate.vote_cnt = candidate.vote_cnt + 1
            candidate.save()
            voter.voter_state = True
            voter.save()
            return JsonResponse({
                'message': 'success!',
                'voter_name': voter_name,
                'candidate_name': candidate_name,
                'vote_cnt': candidate.vote_cnt}, status=HTTP_201_CREATED)
        else:  # 이미 투표를 했다면 투표권 X
            return JsonResponse({'message': '투표는 1회만 가능합니다.'}, status=HTTP_409_CONFLICT)
