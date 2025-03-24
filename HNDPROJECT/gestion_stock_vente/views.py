
from django.shortcuts import render,redirect, get_object_or_404
from .models import Commandes,Fournisseur,ProduitCommande,Client,Facture,Categories,Mouvement
from .decorators import pdg_required, magasinier_required, caissiere_required, roles_required
from django.http import JsonResponse,HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .forms import *
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.template.loader import get_template
from .models import Personne  # Importer le modèle Personne
from .forms import UserRegistrationForm  # Importer le formulaire d'inscription
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.html import format_html


# from xhtml2pdf import pisa
import io


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import pdg_required
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Client, Commandes, ProduitCommande, Facture, Mouvement
import json
@pdg_required
@login_required
def dashboard(request):
    try:
        # Statistiques globales
        total_sales = Commandes.objects.count()
        sum_sales = Commandes.objects.aggregate(Sum('total'))['total__sum'] or 0
        total_clients = Client.objects.count()
        total_products = ProduitCommande.objects.count()
        total_out_of_stock = ProduitCommande.objects.filter(quantite_restant=0).count()
        total_fournisseurs = Fournisseur.objects.count()

        # Données des ventes par mois
        current_year = timezone.now().year
        monthly_sales = Commandes.objects.filter(
            date_commande__year=current_year
        ).values('date_commande__month').annotate(
            montant=Sum('total'),
            nombre=Count('id')
        ).order_by('date_commande__month')

        # Préparation des données pour les graphiques
        sales_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                       'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        sales_data = [0] * 12
        sales_count = [0] * 12

        for sale in monthly_sales:
            month_idx = sale['date_commande__month'] - 1
            sales_data[month_idx] = float(sale['montant'] or 0)
            sales_count[month_idx] = sale['nombre']

        # Données pour le graphique des stocks
        stock_data = [
            ProduitCommande.objects.filter(quantite_restant__gt=0).count(),
            ProduitCommande.objects.filter(quantite_restant=0).count()
        ]

        # Dernières commandes
        recent_orders = Commandes.objects.select_related(
            'client', 'produit'
        ).order_by('-date_commande')[:5]

        # Produits en stock faible
        low_stock = ProduitCommande.objects.filter(
            quantite_restant__lt=F('quantite_commande') * 0.2
        ).order_by('quantite_restant')[:5]

        context = {
            # Statistiques des cards
            'total_sales': total_sales,
            'sum_sales': sum_sales,
            'total_clients': total_clients,
            'total_products': total_products,
            'total_out_of_stock': total_out_of_stock,
            'total_fournisseurs': total_fournisseurs,
            
            # Données des graphiques
            'sales_labels': json.dumps(sales_labels),
            'sales_data': json.dumps(sales_data),
            'sales_count': json.dumps(sales_count),
            'stock_data': json.dumps(stock_data),
            
            # Données des tableaux
            'recent_orders': recent_orders,
            'low_stock': low_stock,
            
            # Métadonnées
            'current_date': timezone.now().strftime("%d %B %Y")
        }

        return render(request, 'pdg/dashboard.html', context)

    except Exception as e:
        return render(request, 'pdg/dashboard.html', {
            'error': f"Une erreur s'est produite : {str(e)}",
            'total_sales': 0,
            'sum_sales': 0,
            'total_clients': 0,
            'total_products': 0,
            'total_out_of_stock': 0,
            'total_fournisseurs': 0,
            'current_date': timezone.now().strftime("%d %B %Y")
        })











#MAGASINIER

@login_required

@login_required
@roles_required(['pdg', 'magasinier'])
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'stock/liste_fournisseur.html', {'fournisseurs': fournisseurs})

@login_required
@roles_required(['pdg', 'magasinier'])
def voir_fournisseur(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    produits = [produit.nom for produit in fournisseur.produits.all()]
    return JsonResponse({
        'nom': fournisseur.nom,
        'pays': fournisseur.pays,
        'adresse': fournisseur.adresse,
        'telephone': fournisseur.telephone,
        'produits': produits,
    })

@login_required
@roles_required(['pdg', 'magasinier'])
def modifier_fournisseur(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    if request.method == 'POST':
        form = fournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Fournisseur modifié avec succès.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Erreur dans le formulaire.'})
    else:
        return JsonResponse({
            'nom': fournisseur.nom,
            'pays': fournisseur.pays,
            'adresse': fournisseur.adresse,
            'telephone': fournisseur.telephone,
            'id': fournisseur.id,
        })

@login_required
@roles_required(['pdg', 'magasinier'])
def supprimer_fournisseur(request, fournisseur_id):
    fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
    if request.method == 'POST':
        fournisseur.delete()
        return JsonResponse({'status': 'success', 'message': 'fournisseur supprimé avec succès.'})
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'})

def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = fournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'fournisseur ajouté avec succès')
            return redirect('liste_fournisseurs')
        else:
            messages.error(request, "Une erreur c'est produite.")
    else:
        form = fournisseurForm()
    return render(request, 'stock/ajouter_fournisseur.html', {'form': form})



@login_required
@magasinier_required
def list_commandes_fournisseur(request):
    commande_fournisseurs = ProduitCommande.objects.all()
    return render(request, 'stock/list_commandes_fournisseur.html', {'commande_fournisseurs': commande_fournisseurs})
 

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import ProduitCommande, Mouvement
from .forms import ProduitCommandeForm  # Assurez-vous d'importer le bon formulaire

@login_required
@magasinier_required
def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitCommandeForm(request.POST)  # Récupérer les données du formulaire
        if form.is_valid():
            produit = form.save(commit=False)  # Créer une instance de produit sans sauvegarde immédiate
            # La quantité restante est initialement égale à la quantité reçue
            produit.quantite_restant = produit.quantite_recu
            produit.save()  # Sauvegarder le produit

            # Enregistrer le mouvement d'entrée
            Mouvement.objects.create(
                produit=produit,
                quantite=produit.quantite_recu,
                type_mouvement='ENTREE'  # Type de mouvement est bien une entrée
            )

            messages.success(request, 'Produit ajouté avec succès et mouvement enregistré.')
            return redirect('produits')  # Rediriger vers la liste des produits
        else:
            # Gérer les erreurs du formulaire
            error_messages = " ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            messages.error(request, format_html("Une erreur s'est produite : {}", error_messages))
    else:
        form = ProduitCommandeForm()  # Créer un formulaire vide

    return render(request, 'stock/ajouterProduit.html', {'form': form})  # Rendre le template avec le formulaire


@login_required
@roles_required(['pdg', 'magasinier'])
def Article(request):
    produits = ProduitCommande.objects.all()  # Récupérer tous les produits
    return render(request, 'stock/listProduit.html',{'produits': produits})



@login_required
@magasinier_required
def ajouter_categorie(request):
    if request.method == 'POST':
        form = categorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Nouvelle catégorie ajoutés avec succès')
            return redirect('afficher_categorie')
        else:
            messages.error(request, "Une erreur c'est produite.")
    else:
        form = categorieForm()
    return render(request,"stock/ajouterCategorie.html", {'form': form})


def afficher_categorie(request):
    categories = Categories.objects.all()
    return render(request, "stock/listeCategorie.html", {'categories': categories})


from django.shortcuts import render
from django.contrib import messages
from .models import Mouvement, ProduitCommande

def mouvement_list(request):
    mouvements = Mouvement.objects.all().select_related('produit')
    stock = {}
    alertes = []  # Pour stocker les alertes de seuil

    # Calculer le stock en temps réel
    mouvements_avec_stock = []  # Liste pour stocker les mouvements avec la quantité restante

    for mouvement in mouvements:
        produit_id = mouvement.produit.id

        # Vérifier si le produit est déjà dans le stock
        if produit_id not in stock:
            # Récupérer la quantité initiale reçue pour le produit
            produit_commande = ProduitCommande.objects.get(id=produit_id)
            stock[produit_id] = produit_commande.quantite_recu  # Quantité initiale

        # Mettre à jour le stock en fonction du type de mouvement
        if mouvement.type_mouvement == 'ENTREE':
            stock[produit_id] += mouvement.quantite  # Ajouter la quantité d'entrée
        elif mouvement.type_mouvement == 'SORTIE':
            stock[produit_id] -= mouvement.quantite  # Soustraire la quantité de sortie

        # Ajouter les détails du mouvement avec la quantité restante à la liste
        mouvements_avec_stock.append({
            'mouvement': mouvement,
            'quantite_restant': stock[produit_id]
        })

        # Vérifier si le stock est à 50 ou moins pour l'alerte
        if stock[produit_id] <= 50:
            produit = ProduitCommande.objects.get(id=produit_id)
            alertes.append(f"Alerte : Le produit '{produit.nom}' est à 50 ou moins. Veuillez renouveler.")

    # Ajouter les alertes à la session
    for alerte in alertes:
        messages.warning(request, alerte)

    return render(request, 'stock/Mouvement_stock.html', {'mouvements': mouvements_avec_stock})



#VENTES




@login_required
@roles_required(['pdg', 'caissière'])
def liste_commandes(request):
    clients = Client.objects.prefetch_related('commandes_set__produit').all()
    return render(request, 'ventes/liste_commande.html', {'clients': clients})


@login_required
def commande(request):
    if request.method == 'POST':
        try:
            client_id = request.POST.get('client')
            client = get_object_or_404(Client, id=client_id)
            produits = request.POST.getlist('produit')
            quantities = request.POST.getlist('quantity')
            specifications = request.POST.getlist('specification')

            for produit_id, quantity, specification in zip(produits, quantities, specifications):
                produit = get_object_or_404(ProduitCommande, id=produit_id)
                quantity = int(quantity)

                # Vérifier le stock disponible
                if produit.quantite_restant < quantity:
                    messages.error(request, 
                        f'Stock insuffisant pour "{produit.nom}" (Disponible: {produit.quantite_restant})')
                    return redirect('commande')

                # Créer la commande
                commande = Commandes.objects.create(
                    produit=produit,
                    quantity=quantity,
                    total=produit.prix_vente * quantity,
                    Specification=specification,
                    client=client
                )

                # Créer le mouvement de sortie
                Mouvement.objects.create(
                    produit=produit,
                    quantite=quantity,
                    type_mouvement='SORTIE'
                )

                # Mettre à jour le stock
                produit.quantite_restant -= quantity
                produit.save()

            messages.success(request, 'Commande enregistrée avec succès.')
        
        except Exception as e:
            messages.error(request, f'Erreur lors de la commande: {str(e)}')
            return redirect('commande')

    # GET request
    clients = Client.objects.all()
    produits = ProduitCommande.objects.filter(quantite_restant__gt=0)
    return render(request, 'ventes/commande.html', {
        'Produit_object': produits, 
        'clients': clients
    })
@login_required
@roles_required(['pdg', 'caissière'])
def generate_facture(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    commandes = client.commandes_set.all()
    montant_total = sum(commande.total for commande in commandes)

    # Créer la facture
    commandes_info = "\n".join([f"Produit: {commande.produit.nom}, Quantité: {commande.quantity}, Prix Unitaire: {commande.produit.prix_vente} FCFA, Total: {commande.total} FCFA, Spécification: {commande.Specification}" for commande in commandes])
    facture = Facture.objects.create(
        client=client,
        montant_total=montant_total,
        enregistre_par=request.user,
        commandes_info=commandes_info
    )

    # Générer le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{facture.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Titre
    title = Paragraph("Facture", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Détails de la facture
    details_data = [
        ["Facture ID:", facture.id],
        ["Date:", facture.date_facture],
        ["Client:", client.nom],
        ["Enregistré par:", facture.enregistre_par.username],
    ]
    details_table = Table(details_data, colWidths=[2 * inch, 4 * inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (1, 0), (1, -1), 12),
        ('BOTTOMPADDING', (1, 0), (1, -1), 6),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 12))

    # Détails de la commande
    commande_data = [
        ["Produit", "Quantité", "Prix Unitaire", "Total", "Spécification"],
    ]
    for commande in commandes:
        commande_data.append([
            commande.produit.nom,
            commande.quantity,
            f"{commande.produit.prix_vente} FCFA",
            f"{commande.total} FCFA",
            commande.Specification
        ])
    commande_table = Table(commande_data, colWidths=[2 * inch, 1 * inch, 1.5 * inch, 1.5 * inch, 2 * inch])
    commande_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(commande_table)
    elements.append(Spacer(1, 12))

    # Montant total
    total_data = [
        ["Montant Total:", f"{facture.montant_total} FCFA"],
    ]
    total_table = Table(total_data, colWidths=[4 * inch, 2 * inch])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 12))

    # Footer
    footer_data = [
        ["Merci pour votre achat!"],
    ]
    footer_table = Table(footer_data, colWidths=[6 * inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    return response





@login_required
def Caissiere(request):
    return render(request, 'ventes/index.html')

 #afficher notre liste des article dans la page d'ajouter un commande 
"""
@login_required
@magasinier_required
def listproduitDefectueux(request):
    Produits_defectueux = Produitdefectueux.objects.all()
    return render(request, 'stock/listDefectueux.html',{'Produits_defectueux': Produits_defectueux})
"""




def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hacher le mot de passe
            user.save()
            login(request, user)  # Connecter l'utilisateur après l'inscription
            messages.success(request, "Votre compte a été créé avec succès.")
            if user.role == 'pdg':
                return redirect('homeAdmin')
            elif user.role == 'magasinier':
                return redirect('mouvement_list')
            elif user.role == 'caissière':
                return redirect('Caissiere')
            else:
                return redirect('home')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def my_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_magasinier:
                return redirect('produits')
            elif user.is_caissiere:
                return redirect('Caissiere')
            else:
                return redirect('homeAdmin')
        else:
            messages.error(request, 'Votre nom d\'utilisateur ou votre mot de passe est incorrect.')
            
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    
    logout(request)
    return redirect('login')

"""
@login_required
@magasinier_required
@pdg_required
def produitDefectueux(request):
    if request.method == 'POST':
        form = ProduitdefectueuxForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Produit   ajouté avec succès')
            return redirect('listDefectueux')
        else:
            messages.error(request, "Une erreur c'est produite.")
    else:
        form = ProduitdefectueuxForm()
    return render(request, 'stock/produitDefectueux.html', {'form': form})
"""
@login_required
def liste_client(request):
    # Utilisez request.user pour accéder aux informations de l'utilisateur connecté
    if request.user.role == 'pdg' or request.user.role == 'caissière':
        clients = Client.objects.all()
        return render(request, 'ventes/liste_clients.html', {'clients': clients})
    else:
        # Si l'utilisateur n'a pas les autorisations requises, redirigez ou montrez un message d'erreur
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('home')  # Remplacez 'home' par la vue appropriée

@login_required
@caissiere_required
def client(request):
    form = clientForm()
    if request.method == 'POST':
        form = clientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Client ajouté avec succès')
            return redirect('liste_clients')
        else:
            messages.error(request, "Une erreur c'est produite.")
    return render(request, 'ventes/client.html', {'form': form})


"""
@login_required
def voir_fournisseur(request, fournisseur_id):
    fournisseurs=fournisseur.objects.filter(id = fournisseur_id)
    print("---------------------------------------------------",fournisseur_id)    
    return render(request, 'stock/voir_fournisseur.html', {'fournisseurs': fournisseurs})

"""
def voir_produit(request, produit_id):
    produits=ProduitCommande.objects.filter(id = produit_id)
    print("---------------------------------------------------",produit_id)    
    return render(request, 'stock/voir_produit.html', {'produits': produits})


@login_required
def modifier_produit(request, produit_id):
    produit_obj = get_object_or_404(Fournisseur, pk=produit_id)
    if request.method == 'POST':
        form = ModifierproduitForm(request.POST, instance=produit_obj)
        if form.is_valid():
            form.save()  # Enregistrer les modifications dans la base de données
            return redirect('voir_produit', fournisseur_id=produit_obj.id)
    else:
        form = ModifierproduitForm(instance=produit_obj)
    return render(request, 'stock/modifier_produit.html', {'form': form, 'produit': produit_obj})


@login_required
def ajouter_article(request):
    if request.method == 'POST':
        form = AjouterArticleForm(request.POST)
        if form.is_valid():
            produit = form.cleaned_data['Produits']
            quantity = form.cleaned_data['quantity']
            specification = form.cleaned_data['Specification']

            # Vérifier la disponibilité du produit en stock
            if produit.quantite >= quantity:
                # Calculer le prix total
                total = produit.prix * quantity

                # Créer et enregistrer la commande
                vente = Commandes.objects.create(
                    Produits=produit,
                    quantity=quantity,
                    total=total,
                    Specification=specification
                )

                # Mettre à jour la quantité en stock du produit
                produit.quantite -= quantity
                produit.save()

                return redirect('liste_commande')  # Redirection après l'ajout de la commande
            else:
                # Gérer le cas où la quantité demandée est supérieure au stock disponible
                form.add_error('quantity', 'Quantité non disponible en stock.')
    else:
        form = AjouterArticleForm()

    return render(request, 'ventes/ajouter_article.html', {'form': form})
"""
@login_required
def modifier_fournisseur(request, fournisseur_id):
    fournisseur_obj = get_object_or_404(fournisseur, pk=fournisseur_id)
    if request.method == 'POST':
        form = ModifierFournisseurForm(request.POST, instance=fournisseur_obj)
        if form.is_valid():
            form.save()  # Enregistrer les modifications dans la base de données
            return redirect('voir_fournisseur', fournisseur_id=fournisseur_obj.id)
    else:
        form = ModifierFournisseurForm(instance=fournisseur_obj)
    return render(request, 'stock/modifier_fournisseur.html', {'form': form, 'fournisseur': fournisseur_obj})
"""
@login_required
def enregistrer_commandes(request):
    if request.method == 'POST':
        products = request.POST.getlist('product[]')
        quantities = request.POST.getlist('quantity[]')
        descriptions = request.POST.getlist('description[]')

        total_price = 0  # Variable pour calculer le prix total

        try:
            for product_id, quantity, description in zip(products, quantities, descriptions):
                produit = get_object_or_404(ProduitCommande, pk=product_id)
                if produit.quantite >= int(quantity):
                    prix_total = produit.prix * int(quantity)
                    total_price += prix_total
                    commande = Commandes.objects.create(
                        produit=produit,
                        quantity=quantity,
                        Specification=description,
                        total=prix_total
                    )
                    produit.quantite -= int(quantity)
                    produit.save()
                else:
                    messages.error(request, "Quantité non disponible en stock.")
                    return redirect(request.META.get('HTTP_REFERER', 'home'))
            
            messages.success(request, f"Commande enregistrée avec succès. Prix total: {total_price}")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        except ValueError:
            messages.error(request, "Les données entrées ne sont pas valides.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

    
    else:
        return redirect('home')




class Ajouter_nouvelle_facture(View):
    template_name = 'ventes/ajouter_facture.html'

    def get(self, request):
        clients = Client.objects.all()
        commandes = Commandes.objects.all()
        return render(request, self.template_name, {'clients': clients, 'commandes': commandes})
""" 
def generate_facture(request):

    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Facture   ajouté avec succès')
            return redirect('listDefectueux')
        else:
            messages.error(request, "Une erreur c'est produite.")
    else:
        form = FactureForm()
    return render(request, 'ventes/ajouter_facture.html', {'form': form})
"""



def homeAdmin(request):
    products = ProduitCommande.objects.all()
    return render(request, "pdg/dashboard.html", {'products': products})

#CLIENTS
@login_required
@roles_required(['pdg', 'caissière'])
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, 'ventes/liste_clients.html', {'clients': clients})

@login_required
@roles_required(['pdg', 'caissière'])
def voir_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    return JsonResponse({
        'nom': client.nom,
        'email': client.email,
        'telephone': client.telephone,
        'adresse': client.adresse,
    })

@login_required
@roles_required(['pdg', 'caissière'])
def modifier_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        form = clientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Client modifié avec succès.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Erreur dans le formulaire.'})
    else:
        return JsonResponse({
            'nom': client.nom,
            'email': client.email,
            'telephone': client.telephone,
            'adresse': client.adresse,
            'id': client.id,
        })

@login_required
@roles_required(['pdg', 'caissière'])
def supprimer_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    if request.method == 'POST':
        client.delete()
        return JsonResponse({'status': 'success', 'message': 'Client supprimé avec succès.'})
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'})


@login_required
def voir_commande(request, commande_id):
    commande = get_object_or_404(Commandes, id=commande_id)
    return JsonResponse({
        'produit': commande.produit.nom,
        'quantity': commande.quantity,
        'specification': commande.Specification,
        'total': commande.total,
    })

@login_required
def modifier_commande(request, commande_id):
    commande = get_object_or_404(Commandes, id=commande_id)
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        if form.is_valid():
            form.save()
            messages.success(request, "Commande modifiée avec succès.")
            return redirect('liste_commandes')  # Redirige vers la liste des commandes
        else:
            return redirect('liste_commandes')  # Redirige vers la liste des commandes
    return redirect('liste_commandes')  # Redirige vers la liste des commandes si méthode GET

@login_required
def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commandes, id=commande_id)
    if request.method == 'POST':
        commande.delete()
        messages.success(request, "Commande supprimée avec succès.")
        return redirect('liste_commandes')  # Redirige vers la liste des commandes
    return redirect('liste_commandes')  # Redirige vers la liste des commandes
"""
@login_required
def supprimer_fournisseur(request, fournisseur_id):
    fournisseur_obj = fournisseur.objects.get(pk=fournisseur_id)
    fournisseur_obj.delete()
    return redirect('liste_fournisseurs')
"""


def produits_en_rupture(request):
    # Récupérer tous les produits ayant un stock inférieur à 5 et à 10
    ruptures = ProduitCommande.objects.filter(quantite_recu=8)

    # Concaténer les deux listes pour éviter les doublons
    return {'ruptures': ruptures}