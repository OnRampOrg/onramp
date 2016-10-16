from django.contrib.auth.models import User

import logging

logger = logging.getLogger(__name__)

class OnRampAuthenticator(object):

    def authenticate(self, username=None, password=None):
        if not username and not password:
            # make sure we got both a username and password
            return None
        logger.debug("Attempting to authenticate: %s", username)
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Invalid user
            return None
        authenticated = user.check_password(password)
        if authenticated:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None