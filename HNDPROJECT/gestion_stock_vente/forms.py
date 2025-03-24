
# the below code fragment can be found in:
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Personne,Fournisseur, Client,Commandes,Categories,Facture,ProduitCommande


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Personne
        fields = ['username', 'email', 'password', 'confirm_password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")



class ProduitCommandeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProduitCommandeForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })

        # Spécifier le format de date pour les champs de date
        self.fields['date_prevu_livraison'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',  # Utilisation du type date pour le sélecteur de date
        })
        self.fields['date_livraison'].widget = forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',  # Utilisation du type date pour le sélecteur de date
        })

    class Meta:
        model = ProduitCommande
        fields = [
            'nom', 
            'description',
            'prix_achat',
            'prix_vente',
            'quantite_commande', 
            'quantite_recu',
            'date_prevu_livraison',
            'date_livraison',
            'numero_contenaire',
            'fournisseur',
            'categories'
        ]



class fournisseurForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(fournisseurForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
    class Meta:
        model = Fournisseur
        fields = ['nom','pays','adresse','telephone']


"""
class ProduitdefectueuxForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProduitdefectueuxForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
    class Meta:
        model = Produitdefectueux
        fields = ['quantite', 'description','Produits']"
"""

class clientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(clientForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
    class Meta:
        model = Client
        fields = ['nom', 'telephone','adresse']
class AjouterArticleForm(forms.ModelForm):
    class Meta:
        model = Commandes
        fields = ['produit', 'quantity', 'Specification']
        widgets = {
            'Produits': forms.Select(attrs={'class': 'form-control select-product'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'Specification': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'style': 'resize: none;'}),
            'total': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Récupérer les produits disponibles et leurs prix
        produits_choices = [(produit.id, f"{produit.nom} - {produit.prix} FCFA") for produit in ProduitCommande.objects.all()]
        self.fields['Produits'].choices = produits_choices

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get("Produits")
        quantity = cleaned_data.get("quantity")
        if produit and quantity:
            # Calculer le prix total
            cleaned_data['total'] = produit.prix * quantity
        return cleaned_data

class ModifierFournisseurForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModifierFournisseurForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
    class Meta:
        model = Fournisseur
        fields = ['nom', 'adresse', 'telephone']




class ModifierproduitForm(forms.ModelForm):
    class Meta:
        model = ProduitCommande
        fields = ['nom', 'description','prix_achat','prix_vente','quantite_commande', 'quantite_recu','date_prevu_livraison','date_livraison','numero_contenaire','fournisseur','categories']




class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commandes
        fields = ['produit', 'Specification', 'quantity', 'total', 'client']

class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = ['montant_total', 'client', 'enregistre_par','commandes_info']
class categorieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(categorieForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
    
    class Meta:
        model = Categories
        fields = ("nom","description")

