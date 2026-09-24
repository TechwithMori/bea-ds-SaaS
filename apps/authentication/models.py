"""Custom user model for merchant accounts."""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from apps.common.models import UUIDModel


class UserManager(BaseUserManager["User"]):
    """Create users with email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: object) -> User:
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> User:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: object) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(UUIDModel, AbstractUser):
    """Merchant operator. Store ownership lives on Tenant, not on this model."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        ordering = ("email",)

    def __str__(self) -> str:
        return self.email
