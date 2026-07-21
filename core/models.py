from django.db import models


class User(models.Model):
    user_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Worker(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    class Type(models.TextChoices):
        INCOME = 'income', 'Доход'
        EXPENSE = 'expense', 'Расход'
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=Type.choices)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True)
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} - {self.category} - {self.amount}"
