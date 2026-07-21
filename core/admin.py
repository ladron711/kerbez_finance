from django.contrib import admin
from .models import User, Worker, Category, Transaction


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "user_id")
    search_fields = ("name",)


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type")
    list_filter = ("type",)
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "category", "worker", "amount")
    list_filter = ("category__type", "category", "worker", "created_at")
    search_fields = ("comment",)
    date_hierarchy = "created_at"