'''
Purpose: enables authentication with EE for ESPA
Author: David V. Hill
'''

import logging
import traceback

from django.contrib.auth.models import User

from ..ordering.models import UserProfile
from ..ordering import lta


logger = logging.getLogger(__name__)


class EEAuthBackend(object):
    '''
    Django authentication system plugin to authenticate against the
    Earth Explorer Registration Service.

    Once authenticated, if the user does not exist in Django it will be
    created.  This is necessary for Django to enforce authentication
    & authorization as well as capturing user related info such as
    the EE contact id, email address and user firstname & lastname
    '''

    def authenticate(self, username=None, password=None):

        #strip whitespace to save users from accidental fat-fingering
        if username is not None:
            username = str(username).strip()
            
        if password is not None:
            password = str(password).strip()

        try:
            contactid = lta.login_user(username, password)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from RegistrationServiceClient will.
                user = User(username=username, password='this isnt used')
                user.is_staff = False
                user.is_superuser = False
                user.save()

                UserProfile(contactid=contactid, user=user).save()

            #check to make sure we have the current user info
            info = lta.get_user_info(username, password)

            save_user = False

            if not user.email or user.email is not info.email:
                user.email = info.email
                save_user = True

            if not user.first_name or user.first_name is not info.first_name:
                user.first_name = info.first_name
                save_user = True

            if not user.last_name or user.last_name is not info.last_name:
                user.last_name = info.last_name
                save_user = True

            if save_user:
                user.save()

            #make sure there is a user profile
            try:
                user.userprofile
            except UserProfile.DoesNotExist:
                UserProfile(contactid=contactid, user=user).save()

            return user
        except Exception:
            
            logger.exception('Exception retrieving user[{0}] from earth '
                             'explorer during login'.format(username))
            logger.debug(traceback.format_exc())

            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
