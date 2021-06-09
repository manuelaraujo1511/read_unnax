from django.http import response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, ProcessScrapingSerialize
from .models import *
from .tasks import t_startProcess
from celery.result import AsyncResult
from .db_con import * 

import json
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    

class ProcessScraping(APIView):
    serializer_class = ProcessScrapingSerialize
    def post(self, request):
        serializer = self.serializer_class(data=request.data)    
        if serializer.is_valid():
            try:
                # Run taks 
                task = t_startProcess.delay(username = request.data['username'], password = request.data['password'], code = request.data['code'])
                res = AsyncResult(task.id)
                
                task_dict = {"task_id": task.id, 'code': request.data['code']}
                
                # Insert to mongo db 
                con = DBConnection()
                
                con.connect()
                con.get_collection('api_transaction')
                api_transaction = con.collect
                api_transaction.insert_one(task_dict)
                
                
                con.close()
                
                return Response({"statutus": res.status}, status=status.HTTP_201_CREATED)

            except Exception as e:
                # Error 
                res = AsyncResult(task.id)
                return Response({'error': True, 'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Error valid serializer
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def StatusProcess(request, code):
    if request.method == 'GET':        
        con = DBConnection()

        con.connect()
        con.get_collection('api_transaction')
        api_transaction = con.collect
        result = api_transaction.find_one({ "code": code })
        if result is not None:
            res = AsyncResult(result['task_id'])
            if res.status == 'FAILURE':
                resp = {
                    'status' : res.status,
                    'data' : str(res.result.args[5])
                }
            
                return Response(resp, status= status.HTTP_202_ACCEPTED)
            elif res.status == 'SUCCESS':
                accounts = [x['accounts_data'] for x in res.result]
                customer = [x['customer_data'] for x in res.result]
                statements = [x['statements_data'] for x in res.result]
                resp = {
                    'status' : res.status,
                    'data' : {
                        'accounts': accounts,
                        'customer': customer,
                        'statements': statements
                    }
                }
                
                # Inser data response to MongoDB
                con = DBConnection()
                
                con.connect()
                con.get_collection('api_result')
                api_result = con.collect
                dic_result = resp
                dic_result['code'] = code
                insert = {'response':resp}
                api_result.insert_one(insert)               
                
                con.close()
            
                return Response(resp)
            else:
                return Response({'status': res.status})
        else:
            return Response({'code': "%s don't exists" % code}, status= status.HTTP_400_BAD_REQUEST)

