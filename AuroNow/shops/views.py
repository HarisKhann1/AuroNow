from django.http import HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist

# Create your views here.
# def hello(request):
#     try:
#         return render(request, 'hello.html')
#     except TemplateDoesNotExist:
#         return HttpResponse("Template not found", status=404)
    
def hello(request):
    try:
        return render(request, 'base_dashboard.html')
    except TemplateDoesNotExist:
        return HttpResponse("Template not found", status=404)
