from django.db import models
from django.core.exceptions import ValidationError


class RecreativeElement(models.Model):

    """
    Represents a recreational item available for reservation in the system.

    Attributes:
        id (str): Unique identifier code for the item (primary key)
        name (str): Name/description of the recreational item
        quantity (int): Total available quantity of this item
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False, null = False, db_column='name')
    quantity = models.IntegerField(blank=False, null = False, db_column='quantity')


    class Meta:
        verbose_name = 'Recreational Item'
        verbose_name_plural = 'Recreational Items'
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name='quantity_non_negative'
            ),
        ]

    def __str__(self):
            return f"{self.id} - {self.name}"

    def clean(self):
        """
        Validates the recreational item data before saving.

        Raises:
            ValidationError: If any field fails validation
        """
        super().clean()

        if not self.name.strip():
            raise ValidationError(
                {'name': 'Item name cannot be empty or whitespace'}
            )

        if self.quantity < 0:
            raise ValidationError(
                {'quantity': 'Quantity cannot be negative'}
            )