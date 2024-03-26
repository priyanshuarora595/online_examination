from django.db import models
from django.utils import timezone
from student.models import Student
from organization.models import Organization

from django.contrib.auth.models import User

import uuid


class Course(models.Model):
    course_name = models.CharField(max_length=50)
    question_number = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    access_code = models.UUIDField(default=uuid.uuid4)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.course_name


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField(default=1)
    question = models.CharField(max_length=1500)
    question_image = models.ImageField(upload_to="image/Exam/", null=True, blank=True)

    @classmethod
    def get_random(cls, course, n=100):
        """Returns a number of random objects. Pass number when calling"""

        import random

        n = int(n)  # Number of objects to return
        last = cls.objects.count()

        selection = random.sample(range(0, last), n)
        selected_ids = []
        selected_objects = []
        for each in selection:
            selected_objects.append(cls.objects.all().filter(course=course)[each])
            selected_ids.append(selected_objects[-1].id)
        # print(selected_ids)
        return selected_objects, selection, selected_ids

    @classmethod
    def get_from_list(cls, course, id_list):
        selected_objects = []
        for each in id_list:
            # selected_objects.append(cls.objects.all().filter(course=course).filter(id=each))
            selected_objects.append(cls.objects.all().filter(course=course)[each])
        # print(selected_objects)
        return selected_objects


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=200)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Option, on_delete=models.CASCADE)


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    status = models.CharField(max_length=10)
    percentage = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)
