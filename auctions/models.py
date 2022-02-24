from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass

class Listing(models.Model):
    item_name = models.CharField(max_length=64)
    item_description = models.CharField(max_length=200)
    item_category = models.CharField(max_length=20)
    start_price = models.DecimalField(max_digits=8, decimal_places=2)
    item_status = models.CharField(max_length=6, choices=[
        ('OPEN','ACTIVE'),
        ('CLOSED','INACTIVE')
        ], default="OPEN")
    item_image = models.URLField(max_length=500)
    item_owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.item_name}'


class Bid(models.Model):
    item_name = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bid_by = models.ForeignKey(User, on_delete=CASCADE)
    current_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f'{self.item_name} - current price : {self.current_price} by {self.bid_by}'


class Comment(models.Model):
    item_name = models.ForeignKey(Listing, on_delete=models.CASCADE)
    item_comments = models.CharField(max_length=200)
    comment_by = models.ForeignKey(User, on_delete=CASCADE)

    def __str__(self):
        return f'{self.comment_by} ({self.item_name}) : {self.item_comments}'

class Watch(models.Model):
    watched_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item_name = models.ForeignKey(Listing, on_delete=models.CASCADE)
    watchlist = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.watched} - {self.item_name} : {self.watchlist}'