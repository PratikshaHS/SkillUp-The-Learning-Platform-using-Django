from django.db import models

class Students(models.Model):
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    phone = models.IntegerField()

    def __str__(self):
        return self.firstname or "Student"
