from django.db import models


class Employees(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(null=True)
    gender = models.CharField(max_length=10,null=True,default=None)
    date_of_birth = models.DateField(null=False)
    industry = models.CharField(max_length=1000,null=True)
    salary = models.FloatField()
    years_of_experience = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"