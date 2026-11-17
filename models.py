from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50)
    discord = fields.CharField(max_length=50)
    name = fields.CharField(max_length=50) #255
    pfp = fields.CharField(max_length=100)
    dorl = fields.BooleanField()
    # age = fields.IntField()

class PlayerCharacter(models.Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()
    name = fields.CharField(max_length=50)
    pfp = fields.CharField(max_length=100)