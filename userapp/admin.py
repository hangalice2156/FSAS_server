from django.contrib import admin
from fcm_django.models import FCMDevice

from . import models

# Register your models here.

admin.site.register(models.building)
admin.site.register(models.node)
admin.site.register(models.floor)
admin.site.register(models.building_to_floor)
admin.site.register(models.floor_to_node)
admin.site.register(models.citizen)
admin.site.register(models.firefighter)
admin.site.register(models.building_user_relation)
