from django.db import models
from accounts.models import Account
from store.models import Product, Variation

class Payment(models.Model):
    payment_id      = models.CharField(max_length=100)
    payment_method  = models.CharField(max_length=100)
    amount_paid     = models.CharField(max_length=100)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)

    user            = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.payment_id

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    # CharFields
    order_number    = models.CharField(max_length=20)
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    phone           = models.CharField(max_length=15)
    addr_1          = models.CharField(max_length=50)
    addr_2          = models.CharField(max_length=50, blank=True)
    city            = models.CharField(max_length=50)
    state           = models.CharField(max_length=50)
    country         = models.CharField(max_length=50)
    order_note      = models.CharField(max_length=150, blank=True)
    status          = models.CharField(max_length=10, choices=STATUS, default='New')
    ip_addr         = models.CharField(max_length=20, blank=True)
    zip_code        = models.CharField(max_length=5, blank=False, null=True)

    # EmailFields
    email           = models.EmailField(max_length=50)

    # FloatFields
    order_total     = models.FloatField()
    tax             = models.FloatField()
    

    # BooleanFields
    is_ordered      = models.BooleanField(default=False)

    # DateTimeFields
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    
    # Foreign Keys
    user            = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment         = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.addr_1}, {self.city}, {self.state}'
        # return f'{self.addr_1}, {self.city}, {self.state}, {self.zip_code}'

    def __str__(self):
        return self.first_name
    
class OrderProduct(models.Model):
    # IntegerField
    quantity                    = models.IntegerField()

    # FloatField
    product_price               = models.FloatField()

    # BooleanFields
    is_ordered                  = models.BooleanField(default=False)

    # DateTimeFields
    created_at                  = models.DateTimeField(auto_now_add=True)
    updated_at                  = models.DateTimeField(auto_now=True)

    # Foreign Keys
    order                       = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    payment                     = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    account                     = models.ForeignKey(Account, on_delete=models.CASCADE)
    product                     = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variation           = models.ForeignKey(Variation, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.product_name
