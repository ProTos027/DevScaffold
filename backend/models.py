from django.db import models

class User(models.Model):
    id= models.UUIDField(primary_key=True)
    username= models.CharField(max_length=50)
    model_chosen= models.CharField(max_length=100)
    api_key= models.CharField(max_length= 100)
    
    provider= models.CharField(max_length=100)
    provider_id= models.CharField(max_length=100)