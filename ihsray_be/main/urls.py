from django.urls import path
from .views import LandingPageAPIView, AdminListCreateView, AdminLoginView, AdminLogoutView, ProductListCreateView, ProductDetailView, SubCategoryListCreateView, SubCategoryDetailView, BannerListCreateView, BannerDetailView, VideoListCreateView, VideoDetailView

urlpatterns = [
    path('landing-page/', LandingPageAPIView.as_view(), name='landing-page'),
    path("admin/create/new/", AdminListCreateView.as_view(), name="admin-list-create"),
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/logout/", AdminLogoutView.as_view(), name="admin-logout"),
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("subcategories/", SubCategoryListCreateView.as_view(), name="sub-category-list-create"),
    path("subcategories/<int:pk>/", SubCategoryDetailView.as_view(), name="sub-category-detail"),
    path("banners/", BannerListCreateView.as_view(), name="banner-list-create"),
    path("banners/<int:pk>/", BannerDetailView.as_view(), name="banner-detail"),
    path("video/", VideoListCreateView.as_view(), name="video-list-create"),
    path("video/<int:pk>/", VideoDetailView.as_view(), name="video-detail"),
]

