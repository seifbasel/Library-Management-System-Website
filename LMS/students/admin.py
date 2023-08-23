from django.contrib import admin

# Register your models here.
from students.models import Student

class StudentID(admin.ModelAdmin):
    readonly_fields = ('id',)
    # list_display = ['name', 'display_borrowed_books']
    # actions = ['display_borrowed_books']

    # def display_borrowed_books(self, request, queryset):
    #     for student in queryset:
    #         borrowed_books_str = student.display_borrowed_books()
    #         self.message_user(request, f"{student.name} borrowed: {borrowed_books_str}")

    # display_borrowed_books.short_description = "Display Borrowed Books"
    
    # list_display = ['name', 'list_borrowed_books']

    # def list_borrowed_books(self, obj):
    #     return ", ".join([book.title for book in obj.borrowed_books.all()])
    
    # list_borrowed_books.short_description = "Borrowed Books"


admin.site.register(Student,StudentID)    
