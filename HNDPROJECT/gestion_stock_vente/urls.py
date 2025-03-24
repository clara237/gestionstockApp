from django.urls import path
from gestion_stock_vente import views

urlpatterns = [
    # STOCK
    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
    path('fournisseurs/voir/<int:fournisseur_id>/', views.voir_fournisseur, name='voir_fournisseur'),
    path('fournisseurs/modifier/<int:fournisseur_id>/', views.modifier_fournisseur, name='modifier_fournisseur'),
    path('fournisseurs/supprimer/<int:fournisseur_id>/', views.supprimer_fournisseur, name='supprimer_fournisseur'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur, name='ajouter_fournisseur'),
    path('list_commandes_fournisseur/', views.list_commandes_fournisseur, name='list_commandes_fournisseur'),
    path('commandes_fournisseur/', views.ajouter_produit, name='commandes_fournisseur'),
    path('produits/', views.ajouter_produit, name='produits'),
    #path('produits/voir/<int:produit_id>/', views.voir_produit, name='voir_produit'),
    path('ajouter_categorie/', views.ajouter_categorie, name='ajouter_categorie'),
    path('afficher_categorie/', views.afficher_categorie, name='afficher_categorie'),
    path('Article', views.Article, name='Article'),
    path('mouvements/', views.mouvement_list, name='mouvement_list'),



      # VENTES
    path('liste_clients/', views.liste_clients, name='liste_clients'),
    path('clients/voir/<int:client_id>/', views.voir_client, name='voir_client'),
    path('clients/modifier/<int:client_id>/', views.modifier_client, name='modifier_client'),
    path('clients/supprimer/<int:client_id>/', views.supprimer_client, name='supprimer_client'),
    path('clients/', views.client, name='client'),
    path('liste_commandes/', views.liste_commandes, name='liste_commande'),
    path('ajouter_article/', views.ajouter_article, name='ajouter_article'),
    path('commande/', views.commande, name='commande'),
    path('generate_facture/<int:client_id>/', views.generate_facture, name='generate_facture'),


    #   PDG
      path('dashboard/', views.dashboard, name='dashboard'),




    # Autres URL
    path('enregistrer_commandes', views.enregistrer_commandes, name='enregistrer_commandes'),
    path('Caissiere', views.Caissiere, name='Caissiere'),
    #path('Magasinier', views.Magasinier, name='Magasinier'),
    #path('mes_produits', views.mes_produits, name='mes_produits'),
    path('register', views.register, name='register'),
    path('', views.my_login, name='login'),
    path('my_logout/', views.logout_user, name='my_logout'),
   # path('produitDefectueux/', views.produitDefectueux, name='produitDefectueux'),
    #path('liste_des_produits_defectueux/', views.listproduitDefectueux, name='listDefectueux'),
    #path('liste_des_produits/', views.liste_des_produits, name='liste_des_produits'),
    path('commandes/<int:commande_id>/modifier/', views.modifier_commande, name='modifier_commande'),
    path('commandes/<int:commande_id>/supprimer/', views.supprimer_commande, name='supprimer_commande'),
    #path('produits/<int:produit_id>/', views.voir_produit, name='voir_produit'),
    path('produits/<int:produit_id>/modifier/', views.modifier_produit, name='modifier_produit'),
    path('homeAdmin/', views.homeAdmin, name='homeAdmin'),
    path('commande/<int:commande_id>/supprimer/', views.supprimer_commande, name='supprimer_commande'),
]