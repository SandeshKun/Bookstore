from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Book, Author, Publisher, Category, BookReview, BookImage

# Custom Admin Actions
def mark_as_featured(modeladmin, request, queryset):
    queryset.update(featured=True)
mark_as_featured.short_description = "Mark selected books as featured"

def mark_as_bestseller(modeladmin, request, queryset):
    queryset.update(bestseller=True)
mark_as_bestseller.short_description = "Mark selected books as bestsellers"

def apply_discount(modeladmin, request, queryset):
    queryset.update(discount_percentage=10)
apply_discount.short_description = "Apply 10% discount to selected books"

# Inline Classes for Related Models
class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ['image_url', 'alt_text', 'is_primary']

class BookReviewInline(admin.TabularInline):
    model = BookReview
    extra = 0
    readonly_fields = ['created_at']
    fields = ['reviewer_name', 'rating', 'title', 'verified_purchase', 'created_at']

# Custom Filters
class StockLevelFilter(admin.SimpleListFilter):
    title = 'Stock Level'
    parameter_name = 'stock_level'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Low Stock'),
            ('out', 'Out of Stock'),
            ('good', 'Good Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock_quantity__lte=5, stock_quantity__gt=0)
        if self.value() == 'out':
            return queryset.filter(stock_quantity=0)
        if self.value() == 'good':
            return queryset.filter(stock_quantity__gt=5)

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('under_20', 'Under $20'),
            ('20_50', '$20 - $50'),
            ('50_100', '$50 - $100'),
            ('over_100', 'Over $100'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'under_20':
            return queryset.filter(price__lt=20)
        if self.value() == '20_50':
            return queryset.filter(price__gte=20, price__lt=50)
        if self.value() == '50_100':
            return queryset.filter(price__gte=50, price__lt=100)
        if self.value() == 'over_100':
            return queryset.filter(price__gte=100)

# Main Model Admin Classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'book_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def book_count(self, obj):
        return obj.book_set.count()
    book_count.short_description = 'Number of Books'

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'book_count', 'birth_date', 'created_at']
    list_filter = ['birth_date', 'created_at']
    search_fields = ['first_name', 'last_name', 'bio']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'birth_date')
        }),
        ('Additional Details', {
            'fields': ('bio', 'website'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def book_count(self, obj):
        return obj.books.count()
    book_count.short_description = 'Books Written'

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'established_year', 'book_count']
    list_filter = ['established_year']
    search_fields = ['name', 'address']
    
    def book_count(self, obj):
        return obj.book_set.count()
    book_count.short_description = 'Books Published'

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'get_authors', 'category', 'price', 'discounted_price_display', 
        'stock_status', 'status', 'featured', 'bestseller'
    ]
    list_filter = [
        'status', 'book_format', 'category', 'featured', 'bestseller', 
        'new_arrival', StockLevelFilter, PriceRangeFilter, 'publication_date'
    ]
    search_fields = ['title', 'isbn_13', 'isbn_10', 'authors__first_name', 'authors__last_name']
    filter_horizontal = ['authors']  # Nice widget for many-to-many
    readonly_fields = ['created_at', 'updated_at', 'average_rating', 'total_reviews']
    
    actions = [mark_as_featured, mark_as_bestseller, apply_discount]
    
    inlines = [BookImageInline, BookReviewInline]
    
    # Organize fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'authors', 'category', 'publisher')
        }),
        ('ISBN & Publication', {
            'fields': ('isbn_10', 'isbn_13', 'publication_date', 'edition', 'language'),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': ('description', 'table_of_contents', 'pages', 'book_format')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'cost_price', 'discount_percentage', 'stock_quantity', 'min_stock_level', 'status'),
            'classes': ('wide',)
        }),
        ('Physical Properties', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        ('Marketing & SEO', {
            'fields': ('featured', 'bestseller', 'new_arrival', 'tags'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('cover_image', 'sample_pdf'),
            'classes': ('collapse',)
        }),
        ('Reviews & Ratings', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display methods
    def get_authors(self, obj):
        authors = obj.authors.all()
        if authors:
            return ", ".join([author.full_name for author in authors])
        return "No authors"
    get_authors.short_description = 'Authors'
    
    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'
    
    def discounted_price_display(self, obj):
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span> <strong style="color: red;">${}</strong>',
                obj.price, obj.discounted_price
            )
        return f"${obj.price}"
    discounted_price_display.short_description = 'Price'
    
    # Custom queryset to optimize database queries
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('authors', 'category', 'publisher')

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'book', 'reviewer_name', 'rating', 'verified_purchase', 'helpful_votes', 'created_at']
    list_filter = ['rating', 'verified_purchase', 'created_at']
    search_fields = ['title', 'book__title', 'reviewer_name', 'review_text']
    readonly_fields = ['created_at']
    list_editable = ['verified_purchase']  # Can edit directly from list view
    
    fieldsets = (
        ('Review Information', {
            'fields': ('book', 'title', 'rating')
        }),
        ('Reviewer Details', {
            'fields': ('reviewer_name', 'reviewer_email', 'verified_purchase')
        }),
        ('Review Content', {
            'fields': ('review_text',)
        }),
        ('Engagement', {
            'fields': ('helpful_votes',)
        }),
        ('System Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ['book', 'image_preview', 'alt_text', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['book__title', 'alt_text']
    readonly_fields = ['created_at']
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" />', obj.image_url)
        return "No image"
    image_preview.short_description = 'Preview'

# Customize Admin Site
admin.site.site_header = "📚 Bookstore Admin"
admin.site.site_title = "Bookstore Admin"
admin.site.index_title = "Welcome to Bookstore Administration"