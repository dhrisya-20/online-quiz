from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Quiz, Question, Result
from .serializers import QuizSerializer, QuestionSerializer
from .chatbot import chatbot_response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import QuestionUserSerializer
from .serializers import QuestionAdminSerializer
from django.utils import timezone
from .serializers import UserSerializer
from datetime import timedelta
from django.utils import timezone


# ==================================================
# PERMISSIONS
# ==================================================

class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


# ==================================================
# AUTH APIs
# ==================================================

@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None or not user.is_admin:
        return Response(
            {"error": "Invalid admin credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "status": "success",
        "role": "admin",
        "data": {
            "admin_id": user.id,
            "username": user.username,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }
    })

@api_view(['GET'])
@permission_classes([IsAdminUserCustom])
def admin_users(request):
    users = User.objects.filter(is_admin=False,is_superuser=False)
    data = UserSerializer(users, many=True).data
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAdminUserCustom])
def admin_results(request):
    results = Result.objects.select_related('user', 'quiz')
    data = []

    for r in results:
        data.append({
            "username": r.user.username,
            "quiz": r.quiz.title,
            "score": r.score,
            "percentage": r.percentage,
            "passed": r.passed
        })

    return Response(data)

@api_view(['DELETE'])
@permission_classes([IsAdminUserCustom])
def delete_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        quiz.delete()
        return Response({"message": "Quiz deleted successfully"})
    except Quiz.DoesNotExist:
        return Response(
            {"error": "Quiz not found"},
            status=404
        )

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    User.objects.create_user(
        username=username,
        password=password,
        is_admin=False
    )

    return Response({"message": "Registered successfully"})


@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None or user.is_admin:
        return Response(
            {"error": "Invalid user credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        "status": "success",
        "role": "user",
        "data": {
            "user_id": user.id,
            "username": user.username,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
        }
    })


# ==================================================
# QUIZ APIs
# ==================================================

@api_view(['POST'])
@permission_classes([IsAdminUserCustom])
def create_quiz(request):
    serializer = QuizSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz(request):
    quizzes = Quiz.objects.filter(is_active=True)
    response = []

    for quiz in quizzes:
        # Python Advanced check
        if quiz.title == "Python Advanced":
            basics_quiz = Quiz.objects.get(title="Python Basics")
            basics_result = Result.objects.filter(
                user=request.user,
                quiz=basics_quiz,
                passed=True
            ).exists()

            if not basics_result:
                continue  # block advanced quiz

        response.append({
            "id": quiz.id,
            "title": quiz.title,
            "time_limit": quiz.time_limit
        })

    return Response(response)


# ==================================================
# QUESTION APIs
# ==================================================

@api_view(['POST'])
@permission_classes([IsAdminUserCustom])
def add_question(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUserCustom])
def update_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return Response({"error": "Question not found"}, status=404)

    serializer = QuestionSerializer(
        question,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Question updated successfully"})
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAdminUserCustom])
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return Response({"message": "Question deleted successfully"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_questions(request, quiz_id):

    quiz = get_object_or_404(Quiz, id=quiz_id)

    # 🔒 Block Python Advanced until Basics passed
    if quiz.title == "Python Advanced":
        basics_quiz = Quiz.objects.get(title="Python Basics")
        passed_basics = Result.objects.filter(
            user=request.user,
            quiz=basics_quiz,
            passed=True
        ).exists()

        if not passed_basics:
            return Response(
                {"error": "You must pass Python Basics to access Python Advanced"},
                status=status.HTTP_403_FORBIDDEN
            )

    questions = Question.objects.filter(quiz=quiz)
    return Response(QuestionUserSerializer(questions, many=True).data)


# ==================================================
# SUBMIT QUIZ
# ==================================================


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz(request):
    quiz_id = request.data.get('quiz_id')
    answers = request.data.get('answers', [])

    quiz = get_object_or_404(Quiz, id=quiz_id)

    # -------------------------------
    # ATTEMPT LOGIC (3 attempts + 24 hrs)
    # -------------------------------
    last_24_hours = timezone.now() - timedelta(hours=24)

    recent_attempts = Result.objects.filter(
        user=request.user,
        quiz=quiz,
        created_at__gte=last_24_hours
    )

    attempts_count = recent_attempts.count()

    # If already passed → block
    if recent_attempts.filter(passed=True).exists():
        return Response(
            {"error": "You have already passed this quiz"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # If 3 attempts used → block for 24 hours
    if attempts_count >= 3:
        return Response(
            {
                "error": "You have used all 3 attempts. Try again after 24 hours."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # -------------------------------
    # EVALUATE QUIZ
    # -------------------------------
    questions = Question.objects.filter(quiz=quiz)
    total_questions = questions.count()

    if total_questions == 0:
        return Response(
            {"error": "No questions available for this quiz"},
            status=status.HTTP_400_BAD_REQUEST
        )

    score = 0

    for ans in answers:
        try:
            q = Question.objects.get(
                id=ans['question_id'],
                quiz=quiz
            )
        except Question.DoesNotExist:
            return Response(
                {"error": f"Invalid question ID {ans['question_id']}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        selected_answer = ans.get('answer')

        valid_options = [
            q.option1,
            q.option2,
            q.option3,
            q.option4
        ]

        if selected_answer not in valid_options:
            return Response(
                {"error": f"Invalid option for question {q.id}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if selected_answer == q.correct_answer:
            score += 1

    percentage = (score / total_questions) * 100
    passed = percentage >= 50

    # -------------------------------
    # SAVE RESULT
    # -------------------------------
    Result.objects.create(
        user=request.user,
        quiz=quiz,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        passed=passed
    )

    # -------------------------------
    # UNLOCK NEXT LEVEL
    # -------------------------------
    if quiz.title == "Python Basics" and passed:
        Quiz.objects.filter(title="Python Advanced").update(is_active=True)

    return Response({
        "quiz": quiz.title,
        "attempt_used": attempts_count + 1,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "passed": passed,
        "remaining_attempts": max(0, 3 - (attempts_count + 1))
    })







# ==================================================
# CHATBOT
# ==================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chatbot(request):
    message = request.data.get('message')

    if not message:
        return Response(
            {"error": "Message is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    reply = chatbot_response(message)
    return Response({"reply": reply})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
