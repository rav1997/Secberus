import datetime
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils.http import base36_to_int
from django.utils.crypto import constant_time_compare
from secberusAPI.constants import ACTIVATION_EMAIL_RESET_TIMEOUT

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )
    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit. Timestamps are rounded to
        # midnight (server time) providing a resolution of only 1 day. If a
        # link is generated 5 minutes before midnight and used 6 minutes later,
        # that counts as 1 day. Therefore, PASSWORD_RESET_TIMEOUT_DAYS = 1 means
        # "at least 1 day, could be up to 2."
        # print(self._num_days(self._today()) - ts)
        if (self._num_days(self._today()) - ts) > int(ACTIVATION_EMAIL_RESET_TIMEOUT*3600):
            return False

        return True

    def _num_days(self, dt):
        return int(dt.strftime("%s"))

    def _today(self):
        # Used for mocking in tests
        return datetime.datetime.now()

account_activation_token = TokenGenerator()
