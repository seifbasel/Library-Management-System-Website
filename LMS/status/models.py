from django.db import models


class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "statuses"

    def __str__(self):
        return f"{self.name}"
