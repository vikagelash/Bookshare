from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=300)
    genre = models.CharField(max_length=100)
    release_year = models.IntegerField()
    # slug = models.SlugField(null=True, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["-id"]

    def __str__(self):
        return self.title
