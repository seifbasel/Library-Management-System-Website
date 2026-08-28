from django import forms


class BorrowForm(forms.Form):
    borrow_period = forms.IntegerField(
        min_value=1,
        max_value=30,
        label="Borrow period (days)",
        help_text="Choose between 1 and 30 days.",
    )
