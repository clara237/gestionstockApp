
"""
class AuthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))  # Rediriger vers la page de connexion
        return self.get_response(request)

class SimpleMiddleware:
    def __init__(self,get_response):
        self.get_response = get_response
        print('hey')
    def __call__(self,request):
        print('heyoo')
        return self.get_response(request)
"""