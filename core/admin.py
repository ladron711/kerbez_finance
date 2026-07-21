from django.contrib import admin
from .models import User, Worker, Category, Transaction


admin.site.register(User)
admin.site.register(Worker)
admin.site.register(Category)
admin.site.register(Transaction)