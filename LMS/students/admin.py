from django.contrib import admin

# Register your models here.
from students.models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'email', 'birthdate', 'user')
    search_fields = ('id',)

admin.site.register(Student, StudentAdmin)
