from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings
from asgiref.sync import async_to_sync

class PersonneManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='magasinier'):
        if not email:
            raise ValueError('Les utilisateurs doivent avoir une adresse e-mail')
        if not username:
            raise ValueError("Les utilisateurs doivent avoir un nom d'utilisateur")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            role=role,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            role='pdg',
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Personne(AbstractBaseUser):
    ROLE_CHOICES = [
        ('magasinier', 'Magasinier'),
        ('caissière', 'Caissière'),
        ('pdg', 'PDG'),
    ]
    
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='magasinier')
    is_magasinier = models.BooleanField(default=False)
    is_caissiere = models.BooleanField(default=False)
    is_pdg = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    objects = PersonneManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def save(self, *args, **kwargs):
        if self.role == 'pdg':
            self.is_pdg = True
            self.is_superuser = True
            self.is_staff = True
        elif self.role == 'magasinier':
            self.is_magasinier = True
        elif self.role == 'caissière':
            self.is_caissiere = True
        super().save(*args, **kwargs)
class Categories(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('date_added',)
        verbose_name = ("Categories")
        verbose_name_plural = ("Categories")


    def __str__(self):
        return self.nom
from django.db import models

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    adresse = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)  # Utiliser CharField pour les numéros de téléphone
    class Meta:
        ordering = ('nom',)
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.nom
    

class ProduitCommande(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix_achat = models.FloatField()  # Prix d'achat du produit
    prix_vente = models.FloatField()   # Prix de vente du produit
    quantite_commande = models.IntegerField()  # Quantité commandée
    quantite_recu = models.IntegerField(default=0)  # Quantité reçue
    quantite_restant = models.IntegerField(default=0)  # Quantité restante
    date_commande = models.DateField(auto_now_add=True)  # Date à laquelle la commande a été faite
    date_prevu_livraison = models.DateField()  # Date prévue de livraison
    date_livraison = models.DateField(null=True, blank=True)  # Date de livraison
    numero_contenaire = models.IntegerField()  # Numéro de conteneur
    fournisseur = models.ForeignKey(Fournisseur, related_name="produits_commandes", on_delete=models.CASCADE)  # Lien vers le fournisseur
    categories = models.ForeignKey(Categories, on_delete=models.CASCADE)  # Lien vers les catégories
    seuil_alerte = models.IntegerField(default=10)

    
   

    class Meta:
        ordering = ('date_commande',)
        verbose_name = "Produit Commande"
        verbose_name_plural = "Produits Commandés"
    
    def update_quantite_restant(self):
        try:
            total_commande = Commandes.objects.filter(produit=self).aggregate(total=models.Sum('quantity'))['total'] or 0
            self.quantite_restant = self.quantite_recu - total_commande
            self.save(update_fields=['quantite_restant'])
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour du stock: {str(e)}")
            return False

    def save(self, *args, **kwargs):
        if self.pk is None:  # Nouveau produit
            self.quantite_restant = self.quantite_recu
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} (Stock: {self.quantite_restant})"


class Commandes(models.Model):
    produit = models.ForeignKey(ProduitCommande, on_delete=models.CASCADE)
    Specification = models.TextField()
    quantity = models.IntegerField()
    total = models.FloatField()
    date_commande = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)  # Ajout du champ client

    class Meta:
        ordering = ('date_commande',)
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande - {self.produit.nom}"
   

    
""" class Produitdefectueux(models.Model):
    quantite=models.IntegerField(default=0)
    description = models.TextField()
    Produits = models.ForeignKey(ProduitCommande, related_name="produitdefectueux", on_delete=models.CASCADE)

    class Meta:
        ordering = ('description',)
        verbose_name = ("Produitdefectueux")
        verbose_name_plural = ("Produitdefectueux")

        def __str__(self):
            return self.description
"""
from django.db import models
from django.utils import timezone
from django import forms

from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.IntegerField()
    adresse = models.CharField(max_length=100)
    email = models.EmailField(default=False)

    class Meta:
        ordering = ('nom',)
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def str(self):
        return self.nom

class Facture(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    date_facture = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    enregistre_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    commandes_info = models.TextField()  # Nouveau champ pour stocker les informations des commandes

    def __str__(self):
        return f"Facture {self.id} pour le client {self.client.nom}"
    


class Mouvement(models.Model):
    TYPE_MOUVEMENT = (
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
    )

    produit = models.ForeignKey(ProduitCommande, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    type_mouvement = models.CharField(max_length=6, choices=TYPE_MOUVEMENT)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produit.nom} - {self.type_mouvement}"