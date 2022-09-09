from datetime import datetime

from peewee import Model, AutoField, CharField, BooleanField, DateTimeField, FloatField, IntegerField

from app.v1.utils.database import dbSql


class User(Model):
    id = AutoField(primary_key=True)
    name = CharField()
    email = CharField(unique=True)
    passwordHash = CharField()
    photo = CharField(null=True)
    isVendor = BooleanField(default=False)
    score = FloatField(null=True)
    ratings = IntegerField(default=0)
    createdAt = DateTimeField(default=datetime.now)
    updatedAt = DateTimeField(default=datetime.now)

    class Meta:
        database = dbSql
        table_name = 'users'

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        return super(User, self).save(*args, **kwargs)
