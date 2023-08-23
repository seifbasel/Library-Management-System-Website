from django.contrib import admin

# Register your models here.
from students.models import Student

class MyModelAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)




admin.site.register(Student,MyModelAdmin)