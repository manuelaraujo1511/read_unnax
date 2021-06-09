from django.contrib.auth.models import User
from .models import *
from rest_framework import serializers
from .db_con import *


class UserSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = User
    fields = ['url', 'username', 'email', 'groups']

class ProcessScrapingSerialize(serializers.Serializer):
  username = serializers.CharField(max_length=128, required = True) 
  password = serializers.CharField(max_length=128, required = True) 
  code = serializers.CharField(max_length=128, required = True)
  def validate_code(self, code):
    """
    Check unique code.
    """
    con = DBConnection()            
    con.connect()
    con.get_collection('api_transaction')
    count = con.collect.count_documents({"code": code})
    con.close()
    if count > 0:
      raise serializers.ValidationError("The code already exists")
    return code

  class Meta:
    model = User 
    fields = ['username', 'password', 'code']
