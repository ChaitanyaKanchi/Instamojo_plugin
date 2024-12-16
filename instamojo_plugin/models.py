from django.db import models

class Payment(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_request_id = models.CharField(max_length=100, null=True, blank=True)  # Keep this if needed

    def __str__(self):
        return f'Payment for {self.name}'
