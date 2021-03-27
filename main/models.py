from django.db import models


class ToiletPaper(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    price = models.IntegerField()
    in_stock = models.IntegerField(default=0)

    description = models.CharField(max_length=500, blank=True, null=True)
    composition = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name
