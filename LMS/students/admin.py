from django.contrib import admin

# Register your models here.
from students.models import Student

class StudentID(admin.ModelAdmin):
    readonly_fields = ('id',)




admin.site.register(Student,StudentID)