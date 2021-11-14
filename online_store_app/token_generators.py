from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.id) + str(user.is_active) + str(timestamp)


email_confirmation_token_generator = EmailConfirmationTokenGenerator()
