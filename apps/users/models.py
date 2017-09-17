# -*- coding: utf-8 -*-
from django.contrib.auth.models import \
    AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.text import slugify

from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator
from post_office import mail

from django_fsm import FSMField, transition

import uuid
from datetime import date
from dateutil.relativedelta import relativedelta


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


class Profile(models.Model):
    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    # Demographics and public profile
    # -------------------------------

    first_name = models.CharField('Prénom', max_length=50)
    last_name = models.CharField('Nom', max_length=100)

    GENDER_CHOICES = (
        ('f', 'Madame'),
        ('m', 'Monsieur'),
        ('na', 'Autre'))
    gender = models.CharField(
        "Genre", choices=GENDER_CHOICES, max_length=10,
        blank=True, null=True)

    common_name = models.CharField(
        "Nom d'usage (si différent)", max_length=100, blank=True, null=True)

    phone_number = PhoneNumberField(
        "Numéro de téléphone", blank=True, null=True)

    birth_date = models.DateField(
        "Date de naissance", blank=True, null=True)

    birth_place = models.CharField(
        "Lieu de naissance", max_length=100, blank=True, null=True)

    death_info = models.CharField(
        "Informations de décès", max_length=200, blank=True, null=True)

    website = models.URLField(
        "Site web", blank=True, null=True)

    phone_number_isvisible = models.NullBooleanField(
        "Numéro de téléphone visible", default=True)
    website_isvisible = models.NullBooleanField(
        "Site web visible", default=True)
    email_isvisible = models.NullBooleanField(
        "Email visible", default=True)

    # Related to the ENS
    # ------------------

    entrance_year = models.IntegerField(
        "Année d'entrée à l'ENS", null=True, blank=False)

    STATUS_SCHOOL_CHOICES = (
        ('inspecteur', 'Élève inspecteur'),
        ('normalien', 'Élève normalien'),
        ('etudiant', 'Étudiant normalien (anciennement auditeur)'),
    )
    status_school = models.CharField(
        "Statut à l'école", max_length=30,
        choices=STATUS_SCHOOL_CHOICES, null=True, blank=False)

    ENTRANCE_SCHOOL_CHOICES = (
        ('ens_lyon', 'ENS de Lyon'),
        ('ens_lsh', 'ENS LSH'),
        ('fontenay', 'Fontenay-aux-Roses'),
        ('st_cloud', 'St Cloud'),
        ('fontenay__st_cloud', 'Fontenay / St Cloud')
    )
    entrance_school = models.CharField(
        "École d'entrée", max_length=30,
        choices=ENTRANCE_SCHOOL_CHOICES, null=True, blank=False)


    ENTRANCE_FIELD_CHOICES = [
        'Allemand',
        'Anglais',
        'Anthropologie',
        'Arabe',
        'Biologie',
        'Chimie',
        'Chinois',
        'Cinéma',
        'Économie',
        'Espagnol',
        'Géographie',
        'Géologie',
        'Histoire de l’art',
        'Histoire',
        'Informatique',
        'Information / Communication',
        'Italien',
        'Lettres classiques',
        'Lettres modernes',
        'Mathématiques',
        'Musique',
        'Philosophie',
        'Physique',
        'Russe',
        'Sciences cognitives',
        'Sciences de l’éducation',
        'Sciences politiques',
        'Sociologie',
        'Théâtre',
    ]
    ENTRANCE_FIELD_CHOICES = [
        (slugify(c), c) for c in ENTRANCE_FIELD_CHOICES]

    entrance_field = models.CharField(
        "Discipline d'entrée", max_length=200,
        choices=ENTRANCE_FIELD_CHOICES, null=True, blank=False)

    PROFESSIONAL_STATUS_CHOICES = (
        ('active', 'Actif'),
        ('retired', 'Retraité'),
        ('student', 'Étudiant'),
        ('inactive', 'Demandeur d\'emploi')
    )
    professional_status = models.CharField(
        "Situation actuelle", max_length=30,
        choices=PROFESSIONAL_STATUS_CHOICES)

    proof_school = models.FileField(
        "Justificatif de passage à l'ENS", upload_to='uploads/%Y/%m/%d/',
        blank=True, null=True)

    # Utilities
    # ---------

    transfer_data = models.NullBooleanField(
        "Transfert des données avec l'ENS de Lyon")

    is_honorary = models.BooleanField("Membre honoraire", default=False)

    do_not_contact = models.BooleanField("Ne pas contacter", default=False)

    annuaire_papier = models.BooleanField(
        "Recevoir l'annuaire en papier", default=False)
    bulletin_papier = models.BooleanField(
        "Recevoir le bulletin en papier", default=False)

    def __str__(self):
        if self.common_name:
            return "{} {}".format(self.first_name, self.common_name)

        return "{} {}".format(self.first_name, self.last_name)

    def type_field(self):
        undef = ['Auditeurs', 'Donateur / Etudiant', 'Etudiant', 'Inspecteur',
                 'Second concours']

        science_fields = [
            'Biologie',  'Biologie, chimie, physique, sciences de la Terre',
            'Chimie', 'Geologie', 'Informatique', 'Mathématiques',
            'Mathématiques, physique', 'Mathématiques-informatique',
            'Physique', 'Physique, chimie', 'Sciences',
            'Sciences de la Vie / de la Terre']

        litt_fields = [
            'Arts', 'Etudiant LSH', 'Langues vivantes',
            'Langues vivantes - Allemand', 'Langues vivantes - Anglais',
            'Langues vivantes - Espagnol', 'Langues vivantes - Italien',
            'Langues vivantes - Russe', 'Langues vivantes-Allemand',
            'Langues vivantes-Anglais', 'Langues vivantes-Espagnol',
            'Langues vivantes-Italien', 'Lettres',
            'Lettres - Lettre classiques', 'Lettres - Lettre modernes',
            'Lettres classiques', 'Lettres et arts', 'Lettres modernes',
            'Sciences economiques et sociales', 'Sciences humaines',
            'Sciences humaines - Histoire & géographie',
            'Sciences humaines - Philosophie',
            'Sciences humaines-géographie', 'Sciences humaines-histoire',
            'Sciences humaines-philosophie',
            'Sciences économiques et sociales', 'lettres', 'lettres et arts',
            'sciences sociales']

        if self.entrance_field in science_fields:
            return 'S'
        elif self.entrance_field in litt_fields:
            return 'L'
        else:
            return ''

    def nomenclature(self):
        if self.entrance_school in ['ens_lyon', 'ens_de_lyon']:
            school = 'LY'
        elif self.entrance_school == 'fontenay':
            school = 'FT'
        elif self.entrance_school == 'st_cloud':
            school = 'SC'
        elif self.entrance_school == 'ens_lsh':
            school = 'SH'
        else:
            school = ''

        field = self.type_field()

        if self.entrance_year:
            promo = str(self.entrance_year)
            return "{} {} {}".format(field, school, promo)

    def expiration_membership(self):
        last = self.membership.first()
        if last is None:
            raise ValueError("No membership was found for user {}".format(self))

        return last.start_date + relativedelta(years=last.duration)

    def active_membership(self):
        last = self.membership.first()
        if last is None:
            return False

        expire = last.start_date + relativedelta(years=last.duration)
        return expire > date.today()


class Address(models.Model):
    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = "Adresses"

    TYPE_CHOICES = (
        ('private_postal', 'Personnelle (privée)'),
        ('public_postal', 'Personnelle (publique)'),
        ('public_non_postal', 'Professionnelle (publique)'),
        ('private_forward', 'Adresse de contact (privée)')
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    type = models.CharField("Type", choices=TYPE_CHOICES, max_length=30)
    line_1 = models.CharField("Ligne 1", max_length=200)
    line_2 = models.CharField("Ligne 2", max_length=200, blank=True)
    postal_code = models.CharField("Code postal", max_length=30)
    city = models.CharField("Commune", max_length=50, blank=False)
    state_province = models.CharField(
        "State/Province", max_length=40, blank=True)
    country = models.CharField("Pays", max_length=40, blank=False)

    def is_public(self):
        return self.type in ['public_postal', 'public_non_postal']


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        db_table = 'auth_user'

    USERNAME_FIELD = 'email'
    objects = UserManager()

    # Generic fields
    email = models.EmailField('Email', max_length=255, unique=True)

    # Generic flags
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    profile = models.OneToOneField(
        Profile, null=True, verbose_name="Profil", related_name='user')

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def get_short_name(self):
        return self.profile.__str__()

    def get_full_name(self):
        return self.profile.__str__()


class Membership(models.Model):
    class Meta:
        verbose_name = "Cotisation"
        verbose_name_plural = "Cotisations"
        ordering = ['-start_date', '-created_on']

    def __str__(self):
        return "Cotisation {} de {}".format(self.start_date.year, self.profile)

    def compute_amount(self, profile=None):
        if profile is None:
            profile = self.profile

        active = self.membership_type == Membership.MEMBERSHIP_TYPE_ACTIVE
        retired = self.membership_type == Membership.MEMBERSHIP_TYPE_RETIRED
        youth = self.membership_type == Membership.MEMBERSHIP_TYPE_YOUTH

        # Up to four years of free membership
        free_membership = self.start_date.year < profile.entrance_year + 4

        if free_membership:
            return 0

        if active:
            return 35 if self.in_couple else 45
        if retired:
            return 30 if self.in_couple else 40
        if youth:
            return 12.50 if self.in_couple else 20

        raise ValueError(
            "Le type de cotisation {} n'est pas "
            "valide.".format(self.membership_type))

    profile = models.ForeignKey(
        Profile, on_delete=models.PROTECT,
        related_name='membership', verbose_name='Utilisateur')

    uid = models.UUIDField(
        "Référence cotisation", unique=True,
        default=uuid.uuid4, editable=False)

    STATUS_TYPE_SUBMITTED = 'submitted'
    STATUS_TYPE_ACCEPTED = 'accepted'
    STATUS_TYPE_REJECTED = 'rejected'

    STATUS_TYPE_CHOICES = (
        (STATUS_TYPE_SUBMITTED, 'Nouvelle demande (paiement en attente)'),
        (STATUS_TYPE_ACCEPTED, 'Demande validée'),
        (STATUS_TYPE_REJECTED, 'Demande rejetée')
    )

    status = FSMField("Statut de la demande", default=STATUS_TYPE_SUBMITTED,
                      choices=STATUS_TYPE_CHOICES)

    # Creation and payment information
    created_on = models.DateTimeField(
        "Date de création", auto_now_add=True)

    # Money transfer
    # --------------

    amount = models.DecimalField(
        "Montant de la cotisation (€)", max_digits=5, decimal_places=2,
        null=True, blank=False)

    payment_amount = models.DecimalField(
        "Montant réglé (€)", max_digits=5, decimal_places=2,
        blank=True, null=True)

    payment_on = models.DateTimeField(
        "Date de réception", blank=True, null=True)

    PAYMENT_TYPE_BANK_TRANSFER = 'BANK_TRANSFER'
    PAYMENT_TYPE_CHECK = 'CHECK'
    PAYMENT_TYPE_CARD = 'CARD'
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_BANK_TRANSFER, 'Virement'),
        (PAYMENT_TYPE_CHECK, 'Chèque'),
        (PAYMENT_TYPE_CARD, 'Carte bancaire')
    )
    payment_type = models.CharField(
        "Méthode de paiment", max_length=30, choices=PAYMENT_TYPE_CHOICES)

    payment_bank = models.CharField(
        "Banque (si applicable)", max_length=100, blank=True)

    payment_reference = models.CharField(
        "Référence chèque ou virement", max_length=100, blank=True)

    payment_name = models.CharField(
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
        "Nom du conjoint", max_length=100, blank=True, null=True)

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

    def is_check(self):
        return self.payment_type == Membership.PAYMENT_TYPE_CHECK

    def is_transfer(self):
        return self.payment_type == Membership.PAYMENT_TYPE_BANK_TRANSFER

    # Transitions
    # -----------

    @transition(field=status, source='submitted', target='rejected',
                custom=dict(button_name="Rejeter la cotisation sans informer l'utilisateur"))
    def reject_silent(self):
        pass

    @transition(field=status, source='submitted', target='rejected',
                custom=dict(button_name="Rejeter la cotisation"))
    def reject(self):
        self.email_user('rejected')

    @transition(field=status, source='submitted', target='accepted',
                custom=dict(button_name="Valider la cotisation"))
    def accept(self):
        self.email_user('accepted')

    def email_user(self, status=None):
        if status is None:
            status = self.status

        mail.send(
            self.profile.user.email,
            'luc@lyon-normalesup.org',  # For development purposes
            template='membership_{}'.format(status),
            context={
                'membership': self
            },
        )
