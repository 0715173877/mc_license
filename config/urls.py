from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/transfer/', include('apps.mrtransferapp.urls')),
    path('api/backoffice/transfer/', include('apps.mrtransferprocessingapp.urls')),
    path('api/enlargement/', include('apps.mrenlargementapp.urls')),
    path('api/backoffice/enlargement/', include('apps.mrenlargementprocessingapp.urls')),
    path('api/surrender/', include('apps.mrsurrenderapp.urls')),
    path('api/backoffice/surrender/', include('apps.mrsurrenderprocessingapp.urls')),
    path('api/pml-tech-support/', include('apps.mrpmltechsupportapp.urls')),
    path('api/backoffice/pml-ts/', include('apps.mrpmltechsupportprocessingapp.urls')),
    path('api/pml-tech-renewal/', include('apps.mrpmltechsupportrenewalapp.urls')),
    path('api/renewal/', include('apps.mrrenewalapp.urls')),
    path('api/complex-shape/', include('apps.mrcomplexshapeapp.urls')),
    path('api/extension/', include('apps.mrextensionapp.urls')),
    path('api/quarterly-report/', include('apps.mrquarterlyreportapp.urls')),
    path('api/cancellation-default/', include('apps.mrcancellationdefaultapp.urls')),
    path('api/suspension/', include('apps.mrsuspensionapp.urls')),

    
    # OpenAPI schema (JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI (interactive docs)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc (alternative UI)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
