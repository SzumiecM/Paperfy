from django.db import models


class ToiletPaper(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    in_stock = models.IntegerField()

    description = models.CharField(max_length=500, default=None)
    composition = models.CharField(max_length=500, default=None)
