from django.db import models

class ListenerState(models.Model):
    name = models.CharField(max_length=255, unique=True, default="block_tracker")
    last_block = models.BigIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.last_block)
    class Meta:
        db_table = 'config'