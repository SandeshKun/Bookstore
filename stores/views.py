from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("It works!")


def show_books(request):
    books = [
        {"title": "Book 1", "author": "Author 1"},
        {"title": "Book 2", "author": "Author 2"},
        {"title": "Book 3", "author": "Author 3"},
    ]
    return render(request, 'books.html', {'books': books})