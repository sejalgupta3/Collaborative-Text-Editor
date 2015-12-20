from django.shortcuts import render, RequestContext
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import TextEditor
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.core import serializers
from docEditor.serializers import EditorSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import JSONParser
from random import randint
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import Application
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
import socket
import psutil
import json
import requests

class Editor:
  id = 0
  dict = None
  textdata = ""

editorList = []
au= []

class EditorView(generics.RetrieveAPIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer, )
    parser_classes = (JSONParser,)
    
    def get_object(self, pk):
        try:
            return TextEditor.objects.get(pk=pk)
        except TextEditor.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        if request.session.get('username'):
			global editorList
			isInList = False
			for editor in editorList:
				if  editor.id == int(pk):
					  isInList = True
					  return render(request, 'login/profile.html', {'editor':editor.textdata,'editorId':editor.id})
			if isInList == False:
				try:
					result =  TextEditor.objects.get(editor_id=pk)
					return render(request, 'login/profile.html', {'editor':result.editor_text,'editorId':result.editor_id})
				except ObjectDoesNotExist:
					return Response({'editor':"",'editorId':pk}, template_name='login/profile.html')
        else:
            return redirect('http://10.0.0.7:8000/login/'+pk)
            
    def post(self, request):
        global editorList
        e1 = Editor()
        e1.id = randint(1,100)
        e1.dict = {}
        data = request.data
        e1.dict[data["lineNumber"]] = data["editorText"]
        e1.textdata = data["textdata"]
        editorList.append(e1)
        return Response({'username':data["username"],'editorId':e1.id,'lineNumber':data["lineNumber"],'editor':e1.dict[data["lineNumber"]]},
        template_name='docEditor/editor.html')

    def put(self, request, pk):
		global editorList
		isInList = False
		for editor in editorList:
			if editor.id == int(pk):
				isInList = True
				editor.dict[request.data["lineNumber"]] = request.data["editorText"]
				editor.textdata = request.data["textdata"]
				e1 = editor
		if isInList == False:
			e1 = Editor
			e1.id = int(pk)
			e1.dict={}
			e1.dict[request.data["lineNumber"]] = request.data["editorText"]
			e1.textdata = request.data["textdata"]
			editorList.append(e1)
                a=request.data["username"]
                if a in au :
                    print ("")
                else:
                    au.append(a)
		dict={'lineNumber':request.data["lineNumber"],'editor':request.data["editorText"],'user':request.data["username"],'eid':pk,'clientId':request.data["clientId"],'au':au}
		print(dict)
		requests.post("http://10.0.0.7:8080/notify",
		json={
			'topic': 'keya.'+'6',
			'args': [dict]
		})
		return Response({'username':request.data["username"],'lineNumber':request.data["lineNumber"],'editor':request.data["editorText"]},
		template_name='docEditor/editor.html')

class EditorSave(generics.RetrieveAPIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer, )
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        try:
             result =  TextEditor.objects.get(editor_id=request.data["idnumber"])
             result.editor_text = request.data["textdata"]
             user_list = result.editor_username.split(",")
             if request.data["username"] not in user_list:
				result.editor_username = result.editor_username + "," +  request.data["username"] 
             result.save()
        except ObjectDoesNotExist:
             text = TextEditor(editor_text=request.data["textdata"], editor_username=request.data["username"], editor_id=int(request.data["idnumber"]))
             text.save()	
        return Response({'username':request.data["username"], 'textdata':request.data["textdata"] ,'idnumber': request.data["idnumber"]},template_name='docEditor/editor.html')

class UserHistory(generics.RetrieveAPIView):
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer, )
    parser_classes = (JSONParser,)
    def post(self, request):
        data = request.data
        result = TextEditor.objects.filter(editor_username__contains=request.data["username"]).values('editor_id', 'editor_text', 'editor_username')
        json_posts = mark_safe(json.dumps(list(result), ensure_ascii=False))
        return Response({'history':json_posts}, template_name='docEditor/editor.html')