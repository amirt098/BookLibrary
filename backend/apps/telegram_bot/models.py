from django.db import models


class Contact(models.Model):
    STATUS_WAITING_FOR_USERNAME = 'waiting_for_username'
    STATUS_REGISTERED = 'status_registered'


    status_choices = (
        (STATUS_WAITING_FOR_USERNAME, "waiting_for_username"),
        (STATUS_REGISTERED, "status_registered"),

    )

    mobile = models.CharField(max_length=15, null=True, blank=True)
    chat_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=50, choices=status_choices, default=STATUS_WAITING_FOR_USERNAME)
