from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import logging

# MODELOS
from .models import Course, Enrollment, Choice, Submission

logger = logging.getLogger(__name__)


# -----------------------------
# AUTH
# -----------------------------
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.info("Nuevo usuario")

        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)

    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


# -----------------------------
# LOGICA DE CURSOS
# -----------------------------
def check_if_enrolled(user, course):
    if user.id is None:
        return False

    return Enrollment.objects.filter(user=user, course=course).exists()


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]

        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)

        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if user.is_authenticated and not check_if_enrolled(user, course):
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(
        reverse('onlinecourse:course_details', args=(course.id,))
    )


# -----------------------------
# EXAMEN
# -----------------------------
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            value = request.POST[key]
            submitted_answers.append(int(value))
    return submitted_answers


def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)

    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)

    choices_ids = extract_answers(request)
    for choice_id in choices_ids:
        choice = Choice.objects.get(id=choice_id)
        submission.choices.add(choice)

    # ✅ Redirigir al resultado en lugar de volver al curso
    return HttpResponseRedirect(
        reverse('onlinecourse:exam_result', args=(course.id, submission.id))
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    # Todas las choices que el usuario seleccionó
    choices = submission.choices.all()

    # Calcular puntaje: choices correctas seleccionadas / total choices correctas * 100
    total_correct = Choice.objects.filter(
        question__course=course, is_correct=True
    ).count()

    selected_correct = sum(
        1 for c in choices if c.is_correct
    )

    # Penalizar respuestas incorrectas seleccionadas
    selected_wrong = sum(
        1 for c in choices if not c.is_correct
    )

    score = max(0, selected_correct - selected_wrong)
    grade = round((score / total_correct) * 100) if total_correct > 0 else 0

    context = {
        'course': course,
        'submission': submission,
        'choices': choices,
        'grade': grade,
    }
    return render(request, 'onlinecourse/course_detail_bootstrap.html', context)
    