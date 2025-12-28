from rest_framework import serializers
from .models import User, Quiz, Question, Result

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_admin']  # 🔒 SAFE

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'

# =======================
# USER QUESTION SERIALIZER (NO ANSWER)
# =======================
class QuestionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['correct_answer']


# =======================
# ADMIN QUESTION SERIALIZER (FULL ACCESS)
# =======================
class QuestionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
