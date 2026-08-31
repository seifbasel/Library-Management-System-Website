from django.contrib import admin

from loans.models import Fine, Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "borrower", "borrowed_at", "due_at", "returned_at", "loan_status")
    list_filter = ("returned_at",)
    search_fields = ("book__title", "borrower__username", "borrower__email")
    autocomplete_fields = ("book", "borrower")
    ordering = ("-created_at",)

    @admin.display(description="Status")
    def loan_status(self, obj):
        return obj.loan_status


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("loan", "amount", "days_overdue", "paid", "created_at")
    list_filter = ("paid",)
    search_fields = ("loan__book__title", "loan__borrower__username")
    autocomplete_fields = ("loan",)
