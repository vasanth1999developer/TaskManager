import email
import random
import string
from django.shortcuts import get_object_or_404, render
from django.core.mail import EmailMessage
import os
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from mytask import serializer
from mytask.models import Role, Task, TaskHistory, User
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail, EmailMessage
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter




from taskmanager.pagination import CustomPagination

class SignUp(APIView):
                   
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        elif self.request.method == 'PUT':
            return [IsAuthenticated()]
        return [IsAuthenticated()]  
    """
    POST method to create a new user
    """
    def post(self, request):
        serialized_data = serializer.UserSerializer(data = request.data)
        if serialized_data.is_valid():
            serialized_data.save()
            return Response(serialized_data.data,status=200)
        return Response({'message': serialized_data.errors},status=401)
     


class RoleApi(APIView):
    """
    Role API to perform CREATE and View operations on Role model
    """
    def post(self, request):
        if request.user.role.name=='Admin':
            serialized_data = serializer.RoleSerializer(data = request.data)
            if serialized_data.is_valid():
                serialized_data.save()
                return Response(serialized_data.data,status=201)
            return Response(serialized_data.errors,status=400)
        return Response({'message': 'Access Denied'}, status=403)     
               

    def get (self,request):
        if request.user.role.name=='Admin':
            roles = Role.objects.all()
            serialized_data = serializer.RoleSerializer(roles, many=True)
            return Response(serialized_data.data,status=200)
        return Response({'message': 'Access Denied'}, status=403)

class AdminCreateUserApi(APIView):
           
       
    """
    AdminCreateUserAction API to perform CREATE by Admin and list operation By Admin and Manager
    """
    def post(self,request):
        if request.user.role.name=='Admin':
            user_data =request.data.copy()
            name_part = ''.join(random.choices(string.ascii_letters, k=4))
            special_char = random.choice("!@#$%&*()+=_-;:?/><[]{}")  
            number_part = ''.join(random.choices(string.digits, k=3))  
            random_string = f"{name_part}{special_char}{number_part}"
            user_data['password'] = random_string 
            serialized_data = serializer.UserSerializer(data = user_data)
            if serialized_data.is_valid():      
                user = serialized_data.save()
                recipient_email = user.email
                Email = EmailMessage(
                            subject='New Task Assignment',
                            body=f"""
                                Hello,{user.user_name}!
                                Your Account has been Created 
                                your password will be {random_string}
                                Best regards,
                                Team
                            """,
                            to=[recipient_email],

                )
                try:
                    Email.send()
                except:
                    print("Failed to send email")
                    return Response({'message': 'Failed to send email'}, status=400)
                return Response(serialized_data.data,status=201)
            return Response(serialized_data.errors,status=400)
        return Response({'message': 'Access Denied'}, status=403)
    
    def get (self,request):
        if request.user.role.name=='Admin'or request.user.role.name=='Manager':
           user= User.objects.filter(role__name='User')
           serialized_data = serializer.UserSerializer(user, many=True)
           return Response(serialized_data.data,status=200)
        return Response({'message': 'Access Denied'}, status=403)


class LoginApi(APIView):
           
    """
    Login API to authenticate a user
    """       
           
    permission_classes = [AllowAny]      
    def post(self, request):          
        client_Auth_Email = request.data['username']
        
        client_Auth_Password = request.data['password']   
        user_instance = User.objects.filter(email=client_Auth_Email.lower()).first()  
        if user_instance is None :
            return Response({'message': 'User Not Found!'}, status=401)
        if not user_instance.check_password(client_Auth_Password):
            return Response({'message': 'Invalid Password!'}, status=401)      
        token, created = Token.objects.get_or_create(user=user_instance)        
        return Response({'token': token.key}, status=200)
    
class TaskApi(APIView):
    """
    Task API to perform POST AND PUT operations on Task model
    """       
    """ 
    POST method to create a Task
    """
    parser_classes = [MultiPartParser, FormParser]       
    def post(self, request):
        if request.user.role.name=='Admin' or request.user.role.name=='Manager':         
            user_instace=request.user
            serialized_data = serializer.TaskSerializer(data=request.data) 
            if serialized_data.is_valid():
                task =serialized_data.save(created_by=user_instace)
                TaskHistory.objects.create(
                    task= task,
                    previous_assignee=None,
                    new_assignee=task.current_assignee,
                    comments=task.comments,
                    picture=task.picture              
                )
                file_path = task.picture.path
                recipient_email = task.current_assignee.email
                Email = EmailMessage(
                            subject='New Task Assignment',
                            body=f"""
                                Hello,
                                A new task has been assigned to you:
                                - Task Title: {task.task_name}
                                - Comments: {task.comments}
                                Please review it at your earliest convenience.
                                Best regards,
                                Team
                            """,
                            to=[recipient_email],
                            bcc=[],
                )
                if file_path and os.path.isfile(file_path):
                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                        Email.attach(os.path.basename(file_path), file_content, 'image/png')
                try:        
                    Email.send()
                except:
                    return Response({"message":"Failed to send email"}, status=400)
                return Response(serialized_data.data, status=200)
            return Response(serialized_data.errors, status=400)
        return Response({'message':'Access denied'}, status=400)
    
    
    """ 
    PUT method to  reassign a Task
    """   
    def put(self, request, pk):
        if request.user.role.name=='User': 
            
            user_id=request.user.id 
            try:
               task_instance = Task.objects.get(pk=pk,current_assignee=user_id,is_deleted=False)
            except:
                return Response({"message":"Invaliduser to Access this Task or Deleted Task"}, status=403)
            previous_assignee = task_instance.current_assignee 
            serialized_data =serializer.TaskSerializer(task_instance, data=request.data, partial=True)
            if serialized_data.is_valid():
                task = serialized_data.save()
                TaskHistory.objects.create(
                    task=task,
                    previous_assignee=previous_assignee,
                    new_assignee=task.current_assignee,
                    comments=request.data.get('comments', ''),
                    picture=task.picture
                )
                file_path = task.picture.path
                recipient_email = task.current_assignee.email
                bcc_recipient = task.created_by.email
                Email = EmailMessage(
                            subject='New Task Assignment',
                            body=f"""
                                Hello,{recipient_email}
                                A new task has been assigned to you:
                                - Task Title: {task.task_name}
                                - Comments: {task.comments}
                                Please review it at your earliest convenience.
                                Best regards,
                                Team
                            """,
                            to=[recipient_email],
                            bcc=[bcc_recipient],
                )
                if file_path and os.path.isfile(file_path):
                        with open(file_path, 'rb') as file:
                            file_content = file.read()
                            Email.attach(os.path.basename(file_path), file_content, 'image/png')
                try:            
                    Email.send()
                except:
                    return Response({"message":"Failed to send email"}, status=400)
                
                return Response(serialized_data.data, status=200)
            return Response(serialized_data.errors, status=403)
     
     
    
    """
    View Task Based on User Profile
    """       
    def get(self, request):
        if request.user.role.name == 'User': 
            user_id = request.user.id       
            tasks = Task.objects.filter(current_assignee=user_id)  
            serialized_tasks = serializer.TaskSerializer(tasks, many=True) 
            return Response(serialized_tasks.data, status=200)         
        return Response({"detail": "Permission denied."}, status=403) 
            

"""
Access to TaskView is only available for Admin and Manager.
"""    
class TaskViewApi(APIView):   
    """View Task Based on Task Pk"""
    def get(self, request,pk):
               
        if request.user.role.name == 'Admin' or request.user.role.name == 'Manager':        
            task = get_object_or_404(Task.objects.prefetch_related('taskhistory_set'), pk=pk)
            serialized_task = serializer.TaskviewSerializer(task)
            return Response(serialized_task.data, status=200)
        return Response({"detail": "Permission denied."}, status=403)

    """ Delete a task  is allowed to delete a task only if the """
    def delete(self,request,pk):
        if request.user.role.name == 'Admin' or request.user.role.name == 'Manager':
            try:       
               task = Task.objects.get(pk=pk)
            except:
                return Response({"message":"Invalid Task to Delete"},status=400)   
            task.is_deleted=True
            task.save()
            return Response({"message":"Task deleted"},status=204)
        else:
            return Response({"detail": "Permission denied."}, status=403)  
    
class TasksView(APIView):
           
    pagination_class=CustomPagination        
    """
    View all Tasks
    Access to TaskView is only available for Admin and Manager.
    """
    def get(self, request):
        if request.user.role.name == 'Admin' or request.user.role.name == 'Manager':        
            tasks = Task.objects.all()
            paginator = self.pagination_class()
            paginated_tasks = paginator.paginate_queryset(tasks, request)
            serialized_tasks = serializer.TaskSerializer(paginated_tasks, many=True)
            return paginator.get_paginated_response(serialized_tasks.data)
        return Response({"detail": "Permission denied."}, status=403)   


    
       
"""
logout of the user 
"""       
class LogoutApi(APIView):
                   
    def post(sefl, request):
        access_token = request.headers.get('Authorization') 
        token = access_token.split(' ')[1]
        token = Token.objects.get(key=token)
        token.delete()
        return Response({"Message":"logged Out.....!"},status=200)
    
    
class TaskListView(ListAPIView):    
   
    serializer_class =serializer.TaskSerializer
    filter_backends =  [SearchFilter]
    search_fields = ['task_name']
    def get_queryset(self):
    
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(created_by=user)  
        return Task.objects.none()