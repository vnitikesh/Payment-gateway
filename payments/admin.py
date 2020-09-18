from django.contrib import admin
from .models import Transaction, Loans

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Loans)
