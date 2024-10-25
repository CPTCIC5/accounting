from django.db import models
from openai import OpenAI
from django.db import transaction
from dotenv import load_dotenv
from django.contrib.auth import get_user_model

load_dotenv()
User= get_user_model()
client= OpenAI()

class Firm(models.Model):
    root_user= models.OneToOneField(User, on_delete= models.CASCADE, related_name='firms')
    
    name= models.CharField(max_length=100)
    address= models.TextField()
    contact_number= models.CharField(max_length=12, unique=True)
    email= models.EmailField(unique=True, null=True, blank=True)
    website_url= models.URLField(unique=True, null=True, blank=True)

    members= models.ManyToManyField(User, blank=True)
    assistant_id = models.CharField(max_length=40,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
         return self.name

    def clean(self):
        super().clean()
        self.website_url= self.website_url.lower()

    def save(self, *args, **kwargs):
        is_being_created = self._state.adding
        super().save(*args, **kwargs)

        if is_being_created:
            assistant= client.beta.assistants.create(
                name=self.name,
                instructions="",
                tools=[{"type": "file_search"}],
                model="gpt-4o"
            )
            self.assistant_id= assistant.id
            self.save(update_fields=['assistant_id'])

            def add_member():
                    self.members.add(self.root_user)

            # https://stackoverflow.com/a/78053539/13953998
            transaction.on_commit(add_member)