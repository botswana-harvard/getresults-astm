from django.db import models
from django.utils import timezone


class SendLog(models.Model):

    result_identifier = models.CharField(
        max_length=25
    )

    destination = models.CharField(
        max_length=25
    )

    sent_datetime = models.DateTimeField(
        default=timezone.now()
    )

    result_json = models.TextField(
        max_length=500,
        null=True
    )

    class Meta:
        app_label = 'getresults_astm'
