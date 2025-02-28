from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password=None, password2=None, first_name = None, last_name = None  ,  **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not password:
            raise ValueError('password is required')
        email = self.normalize_email(email)
        user = self.model(email = email,username = username, first_name = first_name, last_name = last_name , **extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self, username, email, password=None, password2=None, first_name=None ,last_name= None, **extra_fields ):
        user = self.create_user(
            username,
            email,
            password,
            first_name=first_name,
            last_name= last_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
    