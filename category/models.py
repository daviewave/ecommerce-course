from django.db import models

# Create your models here.
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to="photos/categories", blank=True)

    # This controls the display name on the admin page (more so the lower one i believe)
    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    # THIS IS STRICTLY DONE FOR ADMIN PAGE
    def __str__(self):
        return self.category_name
