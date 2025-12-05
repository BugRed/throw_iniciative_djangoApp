from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Página inicial → Login template
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
    
    # API Authentication (JWT)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API REST (v1) - SEPARADO
    path('api/v1/auth/', include('accounts.urls_api')),  # Só API
    path('api/v1/characters/', include('characters.urls')),
    path('api/v1/rooms/', include('rooms.urls')),
    path('api/v1/initiative/', include('initiative.urls')),
    
    # TEMPLATES HTML (Frontend) - SEPARADO
    path('', include('accounts.urls_templates')), 

    
    path('rooms/', include('rooms.urls_templates')),
]