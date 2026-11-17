from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50)     # email account
    discord = fields.CharField(max_length=50)   # discord ID
    name = fields.CharField(max_length=50)      # user name
    pfp = fields.CharField(max_length=100)      # profile picture url
    dorl = fields.BooleanField()                # dark or light mode

class PlayerCharacter(models.Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()                  # user ID of player
    name = fields.CharField(max_length=50)      # character name
    icon = fields.CharField(max_length=100)     # icon picture url
    approved = fields.BooleanField()            # character approved by a DM
    dataappr = fields.JSONField()               # data approved by a DM
    dataunap = fields.JSONField()               # data unapproved by a DM
    datacont = fields.JSONField()               # data controlled entirely by the app

class Party(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)      # party name
    icon = fields.CharField(max_length=100)     # icon picture url
    dataappr = fields.JSONField()               # data approved by a DM
    dataunap = fields.JSONField()               # data unapproved by a DM
    datacont = fields.JSONField()               # data controlled entirely by the app

class Quest(models.Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()                  # user ID of DM
    partyid = fields.IntField()                 # party ID of PCs and NPCs
    name = fields.CharField(max_length=50)      # quest name
    icon = fields.CharField(max_length=100)     # icon picture url
    dataappr = fields.JSONField()               # data approved by a DM
    datacont = fields.JSONField()               # data controlled entirely by the app

class Bastion(models.Model):
    id = fields.IntField(pk=True)
    pcid = fields.IntField()                    # player character ID of sole owner if it has one
    partyid = fields.IntField()                 # party ID of PCs which share ownership
    name = fields.CharField(max_length=50)      # bastion name
    icon = fields.CharField(max_length=100)     # icon picture url
    approved = fields.BooleanField()            # bastion approved by a DM
    dataappr = fields.JSONField()               # data approved by a DM
    dataunap = fields.JSONField()               # data unapproved by a DM
    datacont = fields.JSONField()               # data controlled entirely by the app

class NonPlayerCharacter(models.Model):
    id = fields.IntField(pk=True)
    userid = fields.IntField()                  # user ID of controlling DM if it has one
    pcid = fields.IntField()                    # player character ID of controlling PC if it has one
    name = fields.CharField(max_length=50)      # character name
    icon = fields.CharField(max_length=100)     # icon picture url
    approved = fields.BooleanField()            # character approved by a DM
    dataappr = fields.JSONField()               # data approved by a DM
    dataunap = fields.JSONField()               # data unapproved by a DM
    datacont = fields.JSONField()               # data controlled entirely by the app