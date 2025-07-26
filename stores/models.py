from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    """Book categories like Fiction, Science, History, etc."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"  # Fix plural name in admin
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Author(models.Model):
    """Author information"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, help_text="Author biography")
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Publisher(models.Model):
    """Publishing companies"""
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    established_year = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Book(models.Model):
    """Main Book model with all the details"""
    
    # Basic Info
    title = models.CharField(max_length=300, help_text="Book title")
    subtitle = models.CharField(max_length=300, blank=True)
    isbn_10 = models.CharField(max_length=10, blank=True, unique=True)
    isbn_13 = models.CharField(max_length=13, blank=True, unique=True)
    
    # Relationships
    authors = models.ManyToManyField(Author, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Description & Content
    description = models.TextField(help_text="Book description/summary")
    table_of_contents = models.TextField(blank=True)
    language = models.CharField(max_length=50, default='English')
    
    # Physical Properties
    pages = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in grams")
    dimensions = models.CharField(max_length=50, blank=True, help_text="e.g., 15.2 x 22.9 x 2.5 cm")
    
    # Pricing & Stock
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                            validators=[MinValueValidator(0), MaxValueValidator(100)])
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=5, help_text="Reorder when stock reaches this level")
    
    # Publication Info
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=50, blank=True)
    format_choices = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'E-book'),
        ('audiobook', 'Audiobook'),
    ]
    book_format = models.CharField(max_length=20, choices=format_choices, default='paperback')
    
    # Status & Availability  
    status_choices = [
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
        ('pre_order', 'Pre-order'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='available')
    
    # Rating & Reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                                       validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Images & Media
    cover_image = models.URLField(blank=True, help_text="URL to book cover image")
    sample_pdf = models.URLField(blank=True, help_text="URL to sample PDF")
    
    # SEO & Marketing
    featured = models.BooleanField(default=False, help_text="Show on homepage")
    bestseller = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn_13']),
            models.Index(fields=['status']),
            models.Index(fields=['featured']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def discounted_price(self):
        """Calculate price after discount"""
        if self.discount_percentage > 0:
            discount_amount = (self.price * self.discount_percentage) / 100
            return self.price - discount_amount
        return self.price
    
    @property
    def is_low_stock(self):
        """Check if stock is below minimum level"""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def is_available(self):
        """Check if book is available for purchase"""
        return self.status == 'available' and self.stock_quantity > 0
    
    def get_authors_display(self):
        """Get comma-separated list of authors"""
        return ", ".join([author.full_name for author in self.authors.all()])

class BookReview(models.Model):
    """Customer reviews for books"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField()
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['book', 'reviewer_email']  # One review per email per book
    
    def __str__(self):
        return f"{self.title} - {self.book.title} ({self.rating}/5)"

class BookImage(models.Model):
    """Additional images for books"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"Image for {self.book.title}"