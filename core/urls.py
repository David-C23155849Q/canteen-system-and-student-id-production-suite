from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView # Import this!

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Force the root (/) to go to the login page
    path('', RedirectView.as_view(pattern_name='login'), name='root_redirect'),
    
    # 2. Include all your canteen paths
    path('canteen/', include('canteen.urls')),
]

# Serve media files (Student Photos) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)