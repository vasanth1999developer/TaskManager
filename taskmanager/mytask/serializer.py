from django.forms import ImageField, ValidationError
from rest_framework import serializers

from mytask.models import Role, TaskHistory, User, Task


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer (serializers.ModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)  
    
    class Meta:
        model = User
        fields=['id','user_name','email','password','role']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}  
        }
 
 
    def validate_email(self, value):
        return value.lower()       
    def validate_password(self, password):                
        if len(password) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
                raise serializers.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
                raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
                raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not any(char in '!@#$%&*()+=_-;:?/><[]{},.' for char in password):
                raise serializers.ValidationError("Password must contain at least one special character.")
        return password
                            
    def validate_user_name(self,userName):
        if any(char in '!@#$%^&*()_+{}:"<>?/.,;[]=-1234567890' for char in userName):
                raise serializers.ValidationError("Username cannot contain special characters.")
        return userName
    
    
     
    def create(self, validated_data):
            role_data = validated_data.pop('role', None)  
            password = validated_data.pop('password')
            user = User(**validated_data)
            user.set_password(password)
            if role_data:
                try:
                    role = Role.objects.get(id=role_data.id) 
                except Role.DoesNotExist:
                    raise serializers.ValidationError({"role": "Invalid role ID"})
            else:
                role = Role.objects.get(id=2)
            
            user.role = role
            user.save()
            return user
   
    def update(self, instance, validated_data):
        role_data = validated_data.pop('role', None)
        print(role_data)
        instance = super().update(instance, validated_data)      
        if role_data:
            instance.role = role_data  
            instance.save()                       
        return instance
 
    def get_role(self, obj):
       if obj.role:
            return {
                "id": obj.role.id,
                "name": obj.role.name,
            }
       return None 


def image_validator(image):
    file_size = image.size
    print(file_size)
    mega_byte_limit = 1
    if file_size > mega_byte_limit * 1024 * 1024:
        raise ValidationError('Image size should not exceed 1MB')          


class TaskHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskHistory
        fields = ['id', 'previous_assignee', 'new_assignee', 'comments', 'picture']


class TaskviewSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=False)
    current_assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 
    picture = serializers.ImageField(validators=[image_validator])
    history = TaskHistorySerializer(source='taskhistory_set', many=True, read_only=True)     
    class Meta:
        model = Task
        fields = ['id', 'task_name', 'picture', 'description', 'created_by', 'current_assignee', 'comments', 'status','history']
     
class TaskSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),required=False)
    current_assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 
    picture = serializers.ImageField(validators=[image_validator])
    class Meta:
        model = Task
        fields = ['id', 'task_name', 'picture', 'description', 'created_by', 'current_assignee', 'comments', 'status']
          