from django.db import models
from prospere.contrib.cabinet.models import Documents
from django.contrib.auth.models import User

class Dealings(models.Model):
    buyer = models.ForeignKey(User, related_name='purchase_set')
    seller = models.ForeignKey(User, related_name='selling_set')
    product = models.ForeignKey(Documents)

    cost = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField()

    choices = (
        ('BT', 'Basket'),
        ('PD', 'Purchased'),
        ('WP', 'Waiting pay'),
    )
    state = models.CharField(max_length=2, choices=choices)

    class Meta:
        unique_together = ('buyer', 'product',)
