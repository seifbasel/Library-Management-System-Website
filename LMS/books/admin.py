from django.contrib import admin
from books.models import Book

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author','user', 'status', 'borrow_date', 'borrow_period', "id")
    list_filter = ('status',)
    search_fields = ('title', 'author')



admin.site.register(Book, BookAdmin)
