from django.db import models
from django.contrib.auth.models import User
from organization.models import Organization

from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator

class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(
        max_length = 12,
        null = False,
        validators = [MinLengthValidator(9), MaxLengthValidator(12),RegexValidator('^[+]?[0-9]{9,12}$')],
    )
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name