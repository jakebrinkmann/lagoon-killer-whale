from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    '''Extends the information attached to ESPA users with a one-to-one
    relationship. The other options were to extend the actual Django User
    model or create an entirely new User model.  This is the cleanest and
    recommended method per the Django docs.
    '''
    # reference to the User this Profile belongs to
    user = models.OneToOneField(User)

    # The EE contactid of this user
    contactid = models.CharField(max_length=10)