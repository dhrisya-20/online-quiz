from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Quiz, Question, Result


# =========================
# CUSTOM USER ADMIN
# =========================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'username',
        'email',
        'is_admin',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    list_filter = (
        'is_admin',
        'is_staff',
        'is_superuser',
        'is_active',
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': (
                'is_admin',
                'is_staff',
                'is_superuser',
                'is_active',
                'groups',
                'user_permissions',
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'is_admin',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    search_fields = ('username', 'email')
    ordering = ('username',)


# =========================
# QUIZ ADMIN
# =========================
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'time_limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)


# =========================
# QUESTION ADMIN
# =========================
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'question')
    list_filter = ('quiz',)
    search_fields = ('question',)


# =========================
# RESULT ADMIN
# =========================
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'score')
    list_filter = ('quiz', 'user')
