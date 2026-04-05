from django.contrib import admin
# Importar todos los modelos
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission

# 🔹 Inline para Lesson 
class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# 🔹 Inline para Choice (opciones dentro de preguntas)
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


# 🔹 Inline para Question (preguntas dentro de algo más si se usa luego)
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


# 🔹 Admin de Course
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


# 🔹 Admin de Question (CLAVE 🔥)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]  # aquí metes las opciones dentro de cada pregunta
    list_display = ['content']


# 🔹 Admin de Lesson
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']


# 🔹 Registro de modelos
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)

# 🔥 Nuevos modelos
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)