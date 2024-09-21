from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self, email, password=None, is_staff=False, is_superuser=False, is_active=True
    ):
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError("User must have an password")
        user_obj = self.model(email=self.normalize_email(email))
        user_obj.set_password(password)
        user_obj.is_staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staff(self, email, password=None):
        user_obj = self.create_user(email, password=password, is_staff=True)
        return user_obj

    def create_superuser(self, email, password=None):
        user_obj = self.create_user(
            email, password=password, is_staff=True, is_superuser=True
        )
        return user_obj