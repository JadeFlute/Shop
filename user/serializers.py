from rest_framework import serializers
from .models import users

class Userser(serializers.ModelSerializer):
    class Meta:
        module = users
        fields = ('username','password')