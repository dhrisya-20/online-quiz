from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),

    path('quiz/create/', create_quiz),
    path('quiz/', get_quiz),

    path('question/add/', add_question),
    path('question/<int:quiz_id>/', get_questions),

    path('submit/', submit_quiz),
    path('chatbot/', chatbot),
]
