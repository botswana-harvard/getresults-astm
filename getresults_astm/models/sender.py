from django.db import models


class Sender(models.Model):

    name = models.CharField(
        max_length=25,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_astm'
        db_table = 'getresults_sender'
        ordering = ('name', )
