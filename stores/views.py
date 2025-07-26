from django.shortcuts import render
from django.http import HttpResponse
from .models import Book

def home(request):
    # Show total books and latest additions
    total_books = Book.objects.count()
    latest_books = Book.objects.order_by('-created_at')[:3]
    
    return render(request, 'home.html', {
        'total_books': total_books,
        'latest_books': latest_books
    })

def show_books(request):
    books = Book.objects.all().order_by('title')  # Alphabetical order
    return render(request, 'books.html', {'books': books})

def book_search(request):
    query = request.GET.get('search', '')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    
    return render(request, 'books.html', {
        'books': books, 
        'search_query': query
    })