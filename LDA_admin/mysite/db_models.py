# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    content_type_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'django_content_type'

class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_migrations'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_session'

class GraphLink(models.Model):
    id = models.IntegerField(primary_key=True)
    source = models.ForeignKey('TopicId', db_column='source')
    target = models.IntegerField()
    score = models.FloatField()
    date = models.DateField()
    target_type = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'graph_link'

class GraphNode(models.Model):
    id = models.IntegerField(primary_key=True)
    node_type = models.IntegerField()
    topic = models.ForeignKey('TopicId', blank=True, null=True)
    info = models.CharField(unique=True, max_length=10, blank=True)
    date = models.DateField()
    class Meta:
        managed = False
        db_table = 'graph_node'

class TopicDoc(models.Model):
    id = models.IntegerField(primary_key=True)
    url = models.CharField(unique=True, max_length=250)
    score = models.FloatField()
    title = models.CharField(max_length=250, blank=True)
    stock = models.CharField(max_length=250, blank=True)
    content = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'topic_doc'

class TopicId(models.Model):
    id = models.IntegerField(primary_key=True)
    topic_label = models.ForeignKey('TopicLabel', blank=True, null=True)
    update_time = models.DateTimeField()
    abstract = models.TextField(blank=True)
    sentiment = models.FloatField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    old_concept_label = models.CharField(max_length=300, blank=True)
    class Meta:
        managed = False
        db_table = 'topic_id'

class TopicKeyword(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=10)
    topic = models.ForeignKey(TopicId)
    class Meta:
        managed = False
        db_table = 'topic_keyword'

class TopicLabel(models.Model):
    id = models.IntegerField(primary_key=True)
    label_name = models.CharField(unique=True, max_length=10)
    min_len = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'topic_label'

class TopicLabelWord(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=10)
    word_type = models.IntegerField()
    label = models.ForeignKey(TopicLabel)
    class Meta:
        managed = False
        db_table = 'topic_label_word'

class TopicWord(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=10)
    topic = models.ForeignKey(TopicId)
    is_essential = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'topic_word'

class TopicidDoc(models.Model):
    id = models.BigIntegerField(primary_key=True)
    topic = models.ForeignKey(TopicId)
    topic_doc = models.ForeignKey(TopicDoc)
    series_number = models.IntegerField()
    cluster = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'topicid_doc'

