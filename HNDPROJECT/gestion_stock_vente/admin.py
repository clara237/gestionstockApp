from django.contrib import admin
from .models import *

# Register your models here.
class AdminCategory(admin.ModelAdmin):
    list_display = ('nom', 'description', 'date_added')

class AdminProduitCommande(admin.ModelAdmin):
    list_display = ('nom', 'description','prix_achat','prix_vente','quantite_commande', 'quantite_recu','date_commande','date_prevu_livraison','date_livraison','numero_contenaire','fournisseur','categories' ,'quantite_restant' ,'seuil_alerte')

class AdminCommandes(admin.ModelAdmin):
    list_display = ('Specification','quantity','date_commande','produit','total')


class Adminfournisseur(admin.ModelAdmin):
    list_display = ('nom','pays','adresse','telephone')


#class AdminProduitdefectueux(admin.ModelAdmin):
    #list_display = ( 'quantite', 'description','Produits')

class Adminclient(admin.ModelAdmin):
    list_display = ( 'nom', 'telephone','adresse','email')

class AdminFacture(admin.ModelAdmin):
    list_display = (  'date_facture','montant_total','client','enregistre_par')

class AdminMouvementStock(admin.ModelAdmin):
    list_display = ( 'produit', 'quantite', 'type_mouvement','date')

#admin.site.register(service,Adminfservice)
admin.site.register(Client,Adminclient)
admin.site.register(ProduitCommande,AdminProduitCommande)
admin.site.register(Categories,AdminCategory)
admin.site.register(Commandes,AdminCommandes)
admin.site.register(Personne)
admin.site.register(Fournisseur,Adminfournisseur)
#admin.site.register(Produitdefectueux,AdminProduitdefectueux)
admin.site.register(Facture,AdminFacture)
admin.site.register(Mouvement, AdminMouvementStock)
