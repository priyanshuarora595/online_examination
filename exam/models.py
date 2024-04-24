from django.db import models
from django.utils import timezone
from student.models import Student
from organization.models import Organization

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os


class Course(models.Model):
    course_name = models.CharField(max_length=50)  # name of the course
    question_number = models.PositiveIntegerField(default=0) # number of question in this exam
    total_marks = models.PositiveIntegerField(default=0) # total marks to be awarded in this exam
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE) # exam belongs to which organization
    access_code = models.UUIDField(default=uuid.uuid4) # access code to start the exam
    duration = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1),MaxValueValidator(180)]) # how long the exam will run.
    entry_time = models.PositiveIntegerField(default=30, validators=[MinValueValidator(1), MaxValueValidator(180)]) # time in minutes for how to long to allow participants to start exam.
    passing_percentage = models.PositiveIntegerField(default=75, validators=[MinValueValidator(1), MaxValueValidator(100)]) # passing score criteria
    created_by = models.ForeignKey(User,on_delete=models.CASCADE) # who created the exam
    exam_date = models.DateTimeField() # on which date and time the exam is scheduled

    def __str__(self):
        return self.course_name

def get_image_path(instance, filename):
    return os.path.join('image/Exam', instance.course.course_name, filename)

class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField(default=1, validators=[MinValueValidator((-100)),MaxValueValidator(100)])
    question = models.CharField(max_length=1500)
    question_image = models.ImageField(upload_to=get_image_path, null=True, blank=True)

    @classmethod
    def get_random(cls, course, n):
        """Returns a number of random objects. Pass number when calling"""

        import random

        n = course.question_number  # Number of objects to return
        # last = cls.objects.all().filter(course=course).count()
        last = course.question_number

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
    
    def delete(self,using=None, keep_parents=False):
        if self.question_image:
            self.question_image.delete()
        else:
            pass
        return super().delete(using, keep_parents)


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
