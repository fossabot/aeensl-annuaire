# -*- coding: utf-8 -*-
from django.contrib.auth.models import \
    AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from solo.models import SingletonModel

from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator

import uuid
from datetime import date


class SiteConfiguration(SingletonModel):
    header_message = models.CharField("Bandeau d'avertissement", max_length=255, blank=True)

    def __unicode__(self):
        return u"Configuration du site"

    class Meta:
        verbose_name = "Configuration du site"


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

    USERNAME_FIELD = 'email'
    objects = UserManager()

    # Generic fields
    email = models.EmailField('Email', max_length=255, unique=True)
    password = models.CharField('Mot de passe', max_length=255)

    # Generic flags
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # Demographics and address
    # ------------------------

    first_name = models.CharField('Prénom', max_length=30)
    last_name = models.CharField('Nom', max_length=30)

    birth_name = models.CharField(
        "Nom de naissance", max_length=100, blank=True)

    phone_number = PhoneNumberField("Numéro de téléphone")

    address_line_1 = models.CharField("Ligne 1", max_length=200)
    address_line_2 = models.CharField("Ligne 2", max_length=200, blank=True)
    postal_code = models.CharField("Code postal", max_length=10)
    city = models.CharField("Commune", max_length=50, blank=False)
    state_province = models.CharField(
        "State/Province", max_length=40, blank=True)
    country = models.CharField("Pays", max_length=40, blank=False)

    # Related to the ENS
    # ------------------

    first_year = models.IntegerField("Année d'entrée à l'ENS")

    STATUS_SCHOOL_CHOICES = (
        ('normalien', 'élève normalien'),
        ('etudiant', 'élève étudiant')
    )
    status_school = models.CharField(
        "Status à l'école", max_length=30,
        choices=STATUS_SCHOOL_CHOICES)

    FIELD_CHOICES = (
        ('mathematiques', 'Mathématiques'),
        ('informatique', 'Informatique'),
        ('physique', 'Physique'),
        ('chimie', 'Chimie'),
        ('geographie', 'Géographie')
    )
    field = models.CharField(
        "Discipline d'entrée", max_length=100,
        choices=FIELD_CHOICES)

    PROFESSIONAL_STATUS_CHOICES = (
        ('active', 'actif'),
        ('retired', 'retraité'),
        ('student', 'étudiant'),
        ('inactive', 'sans emploi')
    )
    professional_status = models.CharField(
        "Situation professionnelle actuelle", max_length=30,
        choices=PROFESSIONAL_STATUS_CHOICES)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

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


class Membership(models.Model):
    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"

    def __str__(self):
        return "Cotisation {} de {}".format(self.start_date.year, self.user)

    def compute_amount(self, user=None):
        if user is None:
            user = self.user

        active = self.membership_type == Membership.MEMBERSHIP_TYPE_ACTIVE
        retired = self.membership_type == Membership.MEMBERSHIP_TYPE_RETIRED
        youth = self.membership_type == Membership.MEMBERSHIP_TYPE_YOUTH

        # Up to four years of free membership
        free_membership = self.start_date.year < user.first_year + 4

        if free_membership:
            return 0

        if active:
            return 35 if self.in_couple else 45
        if retired:
            return 30 if self.in_couple else 40
        if youth:
            return 12.50 if self.in_couple else 20

        raise ValueError("Le type de cotisation {} n'est pas valide.".format(self.membership_type))


    user = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='membership', verbose_name='Utilisateur')

    uid = models.UUIDField(
        "Référence cotisation", unique=True,
        default=uuid.uuid4, editable=False)

    STATUS_TYPE_SUBMITTED = 'submitted'
    STATUS_TYPE_ACCEPTED = 'accepted'
    STATUS_TYPE_REJECTED = 'rejected'
    STATUS_TYPE_CHOICES = (
        (STATUS_TYPE_SUBMITTED, 'Demande en cours (paiement en attente)'),
        (STATUS_TYPE_ACCEPTED, 'Demande acceptée (paiement reçu)'),
        (STATUS_TYPE_REJECTED, 'Demande rejetée')
    )
    status = models.CharField(
        "Statut de la demande", max_length=30,
        choices=STATUS_TYPE_CHOICES,
        default=STATUS_TYPE_SUBMITTED)

    # Creation and payment information
    created_on = models.DateTimeField(
        "Date de création", auto_now_add=True)

    # Money transfer
    # --------------

    amount = models.DecimalField(
        "Montant de la cotisation (€)", max_digits=5, decimal_places=2)

    payment_amount = models.DecimalField(
        "Montant réglé (€)", max_digits=5, decimal_places=2,
        blank=True, null=True)

    payment_date = models.DateField(
        "Date de réception", blank=True, null=True)

    PAYMENT_TYPE_BANK_TRANSFER = 'BANK_TRANSFER'
    PAYMENT_TYPE_CHECK = 'CHECK'
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_BANK_TRANSFER, 'Virement'),
        (PAYMENT_TYPE_CHECK, 'Chèque')
    )
    payment_type = models.CharField(
        "Méthode de paiment", max_length=30, choices=PAYMENT_TYPE_CHOICES)

    payment_bank = models.CharField(
        "Banque (si applicable)", max_length=100, blank=True)

    payment_reference = models.CharField(
        "Référence chèque ou virement", max_length=100, blank=True)

    payment_first_name = models.CharField(
        "Prénom (si différent)", max_length=100, blank=True)

    payment_last_name = models.CharField(
        "Nom (si différent)", max_length=100, blank=True)

    # Membership duration
    # -------------------

    start_date = models.DateField(verbose_name="Début de l'adhésion")
    duration = models.PositiveIntegerField(
        "Durée de la cotisation (années civiles)",
        validators=[MinValueValidator(1)], default=1)

    # Other informations
    IN_COUPLE_CHOICES = BOOL_CHOICES = ((True, 'Oui'), (False, 'Non'))
    in_couple = models.BooleanField(
        "Adhésion en couple", choices=IN_COUPLE_CHOICES, default=False)

    partner_name = models.CharField(
        "Nom du conjoint", max_length=100, blank=True)

    MEMBERSHIP_TYPE_ACTIVE = 'active'
    MEMBERSHIP_TYPE_RETIRED = 'retired'
    MEMBERSHIP_TYPE_YOUTH = 'youth'
    MEMBERSHIP_TYPE_CHOICES = (
        (MEMBERSHIP_TYPE_ACTIVE, 'actif'),
        (MEMBERSHIP_TYPE_RETIRED, 'retraité'),
        (MEMBERSHIP_TYPE_YOUTH, 'jeune')
    )
    membership_type = models.CharField(
        "Type de cotisation", max_length=100,
        choices=MEMBERSHIP_TYPE_CHOICES,
        default=MEMBERSHIP_TYPE_ACTIVE)


    def next_start_date(self):
        return date(2017, 1, 1)
