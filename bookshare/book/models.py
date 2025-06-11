from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Book(models.Model):
    title = models.CharField(max_length=250)
    author = models.CharField(max_length=300)
    genre = models.CharField(max_length=100)
    release_year = models.IntegerField()
    slug = models.SlugField(null=True, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    location = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        return super().save(*args, **kwargs)


class Interest(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='interests')
    interested_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_interests')
    request_date = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('book', 'interested_user')
        ordering = ['-request_date']
        verbose_name = "Interest"
        verbose_name_plural = "Interests"

