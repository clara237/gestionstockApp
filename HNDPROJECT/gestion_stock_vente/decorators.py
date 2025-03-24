from django.http import HttpResponseForbidden

def roles_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Vous n'êtes pas autorisé à accéder à cette page.")
        return _wrapped_view
    return decorator

def pdg_required(view_func):
    return roles_required(['pdg'])(view_func)

def magasinier_required(view_func):
    return roles_required(['magasinier'])(view_func)

def caissiere_required(view_func):
    return roles_required(['caissière'])(view_func)