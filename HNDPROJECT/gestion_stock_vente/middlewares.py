from .views import produits_en_rupture

class StockRuptureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Récupérer la liste des produits en rupture de stock
        context = produits_en_rupture(request)
        print("----------------------- :context",context)
        # Ajouter le contexte à chaque requête
        request.stock_rupture_context = context

        response = self.get_response(request)
        print("----------------------- response:", response)

        return response
    