from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Note that you can check your database without runserver with DB Browser for SQLite
# https://sqlitebrowser.org/

#remember to add 'on_delete' attribute if you use foreign key, or your DB may corrupt.

# Reference and setting guildline for imagefield
# https://blog.csdn.net/boycycyzero/article/details/43820481

class building(models.Model):
    building_id = models.CharField(max_length = 100)
    address = models.CharField(max_length = 256)

    def __str__(self):
        return self.building_id

class node(models.Model):
    node_id = models.CharField(max_length = 100)
    posX = models.IntegerField(default=0)
    posY = models.IntegerField(default=0)
    gas = models.CharField(default='null', max_length = 20)
    temperature = models.CharField(default='null', max_length = 20)
    is_alive = models.BooleanField()

    def __str__(self):
        return self.node_id

class floor(models.Model):
    floor_id = models.CharField(max_length = 100)
    floor_plan = models.ImageField(upload_to = 'plans/', height_field=None, width_field=None, max_length=100)
    
    def __str__(self):
        return self.floor_id

class building_to_floor(models.Model):
    bf_id = models.IntegerField(default=0)
    building_id = models.ForeignKey(building, on_delete=models.CASCADE)
    floor_id = models.ForeignKey(floor, on_delete=models.CASCADE)

class floor_to_node(models.Model):
    fn_id = models.IntegerField(default=0)
    floor_id = models.ForeignKey(floor, on_delete=models.CASCADE)
    node_id = models.ForeignKey(node, on_delete=models.CASCADE)

class citizen(models.Model):
    fcm_token = models.CharField(max_length = 256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    building_id = models.ForeignKey(building, on_delete=models.CASCADE)
    floor_number = models.ForeignKey(floor, on_delete=models.CASCADE)

class firefighter(models.Model):
    fcm_token = models.CharField(max_length = 256)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class building_user_relation(models.Model):
    bure_id = models.IntegerField(default=0)
    building = models.ForeignKey(building, on_delete=models.CASCADE)
    account = models.ForeignKey(citizen, on_delete=models.CASCADE)