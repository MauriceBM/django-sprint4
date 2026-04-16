from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from users.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', RegisterView.as_view(),
         name='registration'),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
