from django.db import models

class ListenerState(models.Model):
    last_block = models.BigIntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.last_block)
    class Meta:
        db_table = 'config'