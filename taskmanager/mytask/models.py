from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name   

class User(AbstractBaseUser):      
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role, related_name='users', on_delete=models.SET_NULL, null=True, blank=True)
    USERNAME_FIELD = 'email'              
    def __str__(self):
       return self.email
   
class Task(models.Model):
    task_name = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='picture/%Y/%m/%d',max_length=400,null=True)
    description = models.CharField(max_length=200)
    created_by= models.ForeignKey(User, blank=True, null=True,on_delete=models.SET_NULL,related_name="created_by")
    current_assignee= models.ForeignKey(User, blank=True, null=True,on_delete=models.SET_NULL,related_name="current_Assignee")
    comments =models.CharField(max_length=400, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Pending')
    is_deleted = models.BooleanField(default=False)
    
    
class TaskHistory(models.Model):
     task = models.ForeignKey(Task, on_delete=models.CASCADE)
     previous_assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='previous_assignee')
     new_assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='new_assignee')
     comments = models.CharField(max_length=400, blank=True, null=True)
     picture = models.ImageField(upload_to='picture/%Y/%m/%d',max_length=400,null=True)       
           
        
       
    