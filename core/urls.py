from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

# -------------------------------------------------------------
# 1. Definição Principal de URLS
# -------------------------------------------------------------
urlpatterns = [
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Página inicial
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
    
    # API Authentication (JWT)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API REST (v1)
    path('api/v1/auth/', include('accounts.urls_api')),
    path('api/v1/characters/', include('characters.urls')),
    path('api/v1/rooms/', include('rooms.urls')), 
    path('api/v1/initiative/', include('initiative.urls')),
    
    # TEMPLATES HTML (Frontend)
    path('', include('accounts.urls_templates')), 

    # Aplicando Namespacing para Templates de Salas
    path('rooms/', include('rooms.urls_templates', namespace='room_templates')),
    path('characters/', include('characters.urls_templates')), 
]


# -------------------------------------------------------------
# 2. Configuração de Mídia (SOMENTE EM MODO DEBUG)
# -------------------------------------------------------------
# ISSO DEVE VIR DEPOIS DA DEFINIÇÃO DE urlpatterns = [...]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)