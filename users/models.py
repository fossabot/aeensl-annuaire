# -*- coding: utf-8 -*-
from django.contrib.auth.models import \
    AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator

import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        db_table = 'auth_user'

    email = models.EmailField('Email', max_length=255, unique=True)
    first_name = models.CharField('Prénom', max_length=30)
    last_name = models.CharField('Nom', max_length=30)

    USERNAME_FIELD = 'email'
    objects = UserManager()

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return "{p.first_name} {p.last_name}".format(p=self)

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.__str__()


class Profile(models.Model):
    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, verbose_name='Utilisateur')

    married_name = models.CharField(
        max_length=100, blank=True, verbose_name="Nom de naissance")

    phone_number = PhoneNumberField(verbose_name="Numéro de téléphone")
    address = models.TextField(verbose_name="Adresse postale")

    # Related to the ENS
    first_year = models.IntegerField(verbose_name="Année d'entrée à l'ENS")
    field = models.CharField(
        max_length=100,
        verbose_name="Département d'entrée")
    notes = models.TextField(blank=True, verbose_name="Commentaires divers")


class Membership(models.Model):
    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"

    def __str__(self):
        return "Cotisation {} de {}".format(self.start_date.year, self.user)

    user = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name='Utilisateur')

    models.UUIDField()

    uid = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name='Référence cotisation',
    )

    STATUS_TYPE_SUBMITTED = 'submitted'
    STATUS_TYPE_ACCEPTED = 'accepted'
    STATUS_TYPE_REJECTED = 'rejected'
    STATUS_TYPE_CHOICES = (
        (STATUS_TYPE_SUBMITTED, 'Demande en cours'),
        (STATUS_TYPE_ACCEPTED, 'Cotisation validée'),
        (STATUS_TYPE_REJECTED, 'Demande rejetée')
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_TYPE_CHOICES,
        default=STATUS_TYPE_SUBMITTED,
        verbose_name='Statut de la demande'
    )

    # Creation and payment information
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de création")
    amount = models.DecimalField(max_digits=5, decimal_places=2,
                                 verbose_name='Montant (€)')

    REFERENCE_TYPE_BANK_TRANSFER = 'BANK_TRANSFER'
    REFERENCE_TYPE_CHECK = 'CHECK'
    REFERENCE_TYPE_CASH = 'CASH'
    REFERENCE_TYPE_NONE = 'NONE'
    REFERENCE_TYPE_CHOICES = (
        (REFERENCE_TYPE_BANK_TRANSFER, 'Virement'),
        (REFERENCE_TYPE_CHECK, 'Chèque'),
        (REFERENCE_TYPE_CASH, 'Espèces'),
        (REFERENCE_TYPE_NONE, 'Aucun'),
    )
    reference_type = models.CharField(
        max_length=30,
        choices=REFERENCE_TYPE_CHOICES,
        default=REFERENCE_TYPE_NONE,
        verbose_name='Méthode de paiment'
    )

    # Membership duration
    start_date = models.DateField(verbose_name="Début de l'adhésion")
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    # Other informations
    in_couple = models.BooleanField()
    partner_name = models.CharField(max_length=100, blank=True)

    MEMBERSHIP_TYPE_ACTIVE = 'active'
    MEMBERSHIP_TYPE_RETIRED = 'retired'
    MEMBERSHIP_TYPE_YOUTH = 'youth'
    MEMBERSHIP_TYPE_CHOICES = (
        (MEMBERSHIP_TYPE_ACTIVE, 'actif'),
        (MEMBERSHIP_TYPE_RETIRED, 'retraité'),
        (MEMBERSHIP_TYPE_YOUTH, 'jeune')
    )
    membership_type = models.CharField(
        max_length=100,
        choices=MEMBERSHIP_TYPE_CHOICES,
        default=MEMBERSHIP_TYPE_ACTIVE,
        verbose_name="Type de cotisation")
