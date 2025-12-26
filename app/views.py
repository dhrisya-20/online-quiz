from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate

from .models import User, Quiz, Question, Result
from .serializers import *
from .chatbot import chatbot_response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

# ---------- AUTH ----------
@api_view(['POST'])
def register(request):
    User.objects.create_user(
        username=request.data['username'],
        password=request.data['password'],
        is_admin=request.data.get('is_admin', False)
    )
    return Response({"message": "Registered successfully"})


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 🔐 Create JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin,
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh)
    })


# ---------- QUIZ ----------
@api_view(['POST'])
def create_quiz(request):
    serializer = QuizSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
def get_quiz(request):
    quizzes = Quiz.objects.filter(is_active=True)
    return Response(QuizSerializer(quizzes, many=True).data)


# ---------- QUESTIONS ----------
@api_view(['POST'])
def add_question(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
def get_questions(request, quiz_id):
    questions = Question.objects.filter(quiz_id=quiz_id)
    return Response(QuestionSerializer(questions, many=True).data)


# ---------- SUBMIT ----------
@api_view(['POST'])
def submit_quiz(request):
    score = 0
    for ans in request.data['answers']:
        q = Question.objects.get(id=ans['question_id'])
        if q.correct_answer == ans['answer']:
            score += 1

    Result.objects.create(
        user_id=request.data['user_id'],
        quiz_id=request.data['quiz_id'],
        score=score
    )
    return Response({"score": score})


# ---------- CHATBOT ----------
@api_view(['POST'])
def chatbot(request):
    reply = chatbot_response(request.data['message'])
    return Response({"reply": reply})
