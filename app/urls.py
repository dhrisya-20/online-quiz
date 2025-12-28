from django.urls import path
from .views import *

urlpatterns = [
    path('admin/login/', admin_login),
    path('admin/users/', admin_users),
    path('register/', register),
    path('login/', user_login),
    path('admin/results/', admin_results),
   

    path('quiz/create/', create_quiz),
    path('quiz/', get_quiz),
    path('quiz/delete/<int:quiz_id>/', delete_quiz),


    path('question/add/', add_question),
    path('question/<int:quiz_id>/', get_questions),
     path('question/update/<int:question_id>/', update_question),

    path('question/update/<int:question_id>/', update_question),
    path('question/delete/<int:question_id>/', delete_question),

    path('submit/', submit_quiz),

    path('chatbot/', chatbot),

]
