from django.db import models

# Create your models here.


class Organizations(models.Model):
    organization_id = models.IntegerField()
    name = models.CharField( 
        max_length=100 
    )

    def __str__(self):
        return self.name;
    
    class Meta:
        unique_together = ("organization_id", "name")

class Employees(models.Model):
    employee_id = models.IntegerField()
    name = models.CharField( 
        max_length=100 
    )
    organization_id = models.IntegerField()
    email = models.CharField( 
        max_length=200 
    )
    
    organization_id = models.ForeignKey(
        Organizations,
        related_name='Organization_Employee',
        null=True,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name;
    
    class Meta:
        unique_together = ("employee_id", "name")

class Projects(models.Model):
    project_id = models.IntegerField()
    name = models.CharField(
        max_length=100
    )
    status = models.CharField(
        max_length=255,
        null=True
    )
    description = models.CharField(
        max_length=255, 
        null=True
    )
    organization_id = models.IntegerField()
    organization_id = models.ForeignKey(
        Organizations, 
        related_name='Organization_Project', 
        null=True, 
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name;
    
    class Meta:
        unique_together = ("project_id", "name")


class LogTimes(models.Model):
    project_id = models.IntegerField()
    user_id = models.IntegerField()
    log_date = models.DateField()
    logged_time = models.CharField(
        max_length=100
    )
    project_id = models.ForeignKey(
        Projects, 
        null=True, 
        related_name='project', 
        on_delete=models.CASCADE
    )

    user_id = models.ForeignKey(
        Employees, 
        null=True, 
        related_name='employee', 
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.log_date;
    
    class Meta:
        unique_together = ("project_id", "user_id", "log_date")