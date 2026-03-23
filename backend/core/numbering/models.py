from django.db import models

class NumberingSequence(models.Model):
    module_name = models.CharField(max_length=50, unique=True)
    prefix = models.CharField(max_length=10)
    current_number = models.IntegerField(default=0)
    padding = models.IntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.module_name}: {self.prefix}{str(self.current_number).zfill(self.padding)}"