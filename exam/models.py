from django.db import models
from django.utils import timezone
from student.models import Student
from organization.models import Organization
class Course(models.Model):
   course_name = models.CharField(max_length=50)
   question_number = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField()
   organization = models.ForeignKey(Organization,on_delete=models.CASCADE)
   def __str__(self):
        return self.course_name

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField(default=1)
    question=models.CharField(max_length=1500)
    question_image= models.ImageField(upload_to='image/Exam/',null=True,blank=True)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200,default="None")
    option4=models.CharField(max_length=200,default="None")
    option5=models.CharField(max_length=200,default="None Of the Above")
    option6=models.CharField(max_length=200,default="Can't be determined")
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)
    
    @classmethod
    def get_random(cls,course,n=100):
        """Returns a number of random objects. Pass number when calling"""

        import random
        n = int(n) # Number of objects to return
        last = cls.objects.count()
        
        selection = random.sample(range(0, last), n)
        selected_ids=[]
        selected_objects = []
        for each in selection:
            selected_objects.append(cls.objects.all().filter(course=course)[each])
            selected_ids.append(selected_objects[-1].id)
        # print(selected_ids)
        return selected_objects,selection,selected_ids
    
    @classmethod
    def get_from_list(cls,course,id_list):
        selected_objects = []
        for each in id_list:
            # selected_objects.append(cls.objects.all().filter(course=course).filter(id=each))
            selected_objects.append(cls.objects.all().filter(course=course)[each])
        # print(selected_objects)
        return selected_objects

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    status = models.CharField(max_length=10)
    percentage = models.PositiveIntegerField()
    date = models.DateTimeField(default=timezone.now)

