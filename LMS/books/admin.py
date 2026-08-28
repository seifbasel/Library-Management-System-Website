from django.contrib import admin

from books.models import Book


class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "genre", "status", "is_available_display", "id")
    list_filter = ("status", "genre")
    search_fields = ("title", "author")

    @admin.display(description="Available", boolean=True)
    def is_available_display(self, obj):
        return obj.is_available


admin.site.register(Book, BookAdmin)
