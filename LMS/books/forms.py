from django import forms
from django.core.validators import MaxValueValidator

from organization.models import LibrarySettings


class BorrowForm(forms.Form):
    borrow_period = forms.IntegerField(min_value=1, label="Borrow period (days)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings_obj = LibrarySettings.get_solo()
        default_days = settings_obj.loan_duration_days
        # A generous ceiling above this deployment's default so a customer
        # with a longer standard loan period (e.g. a semester loan) isn't
        # blocked by a hardcoded limit - but still bounded, not unlimited.
        max_days = max(default_days * 3, 30)

        field = self.fields["borrow_period"]
        field.validators.append(MaxValueValidator(max_days))
        field.initial = default_days
        field.help_text = f"Choose between 1 and {max_days} days ({default_days} is the default)."
        field.widget.attrs.update({"min": 1, "max": max_days, "class": "field-input"})
