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
    process_uid = models.CharField(max_length=150, null=True)


class Process(models.Model):
    #process type
    OFFER_BOOK_PROCESS = 'offer_book_process'

    #formal status
    STATUS_FINISHED = 'finished_status'
    STATUS_INITIATE = 'initiate_status'

    uid = models.CharField(max_length=150, unique=True)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=50, null=True)
    step_counter = models.IntegerField(default=0)


class Field(models.Model):
    name = models.CharField(max_length=30)
    value = models.CharField(max_length=50)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
