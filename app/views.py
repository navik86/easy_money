from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    reveal_type(request.is_ajax)
    reveal_type(request.user)
    return render(request, 'main/index.html')