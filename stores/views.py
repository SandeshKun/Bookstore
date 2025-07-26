from django.shortcuts import render
from django.http import HttpResponse
from .models import Book, Author, Category

def home(request):
    # Get statistics
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    total_categories = Category.objects.count()
    
    # Get featured books (limit to 6)
    featured_books = Book.objects.filter(
        featured=True, 
        status='available'
    ).select_related('category').prefetch_related('authors')[:6]
    
    # Get latest books (limit to 6)
    latest_books = Book.objects.filter(
        status='available'
    ).select_related('category').prefetch_related('authors').order_by('-created_at')[:6]
    
    # Get bestsellers (limit to 6)
    bestsellers = Book.objects.filter(
        bestseller=True,
        status='available'
    ).select_related('category').prefetch_related('authors')[:6]
    
    context = {
        'total_books': total_books,
        'total_authors': total_authors,
        'total_categories': total_categories,
        'featured_books': featured_books,
        'latest_books': latest_books,
        'bestsellers': bestsellers,
    }
    
    return render(request, 'home.html', context)

def show_books(request):
    books = Book.objects.filter(
        status='available'
    ).select_related('category').prefetch_related('authors').order_by('title')
    
    return render(request, 'books.html', {'books': books})