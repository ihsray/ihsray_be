from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics,filters,pagination
from .models import Admin, Product, SubCategory, Banner, Video
from .serializers import AdminSerializer, ProductSerializer, SubCategorySerializer, BannerSerializer, VideoSerializer
from .utils import require_admin_authentication
from rest_framework.response import Response
from rest_framework import status

@method_decorator(csrf_exempt, name='dispatch')
class AdminLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({
                "status": "false", 
                "message": "Both fields are required", 
                "statusCode": "001"
                }, status=status.HTTP_400_BAD_REQUEST)

        admin = get_object_or_404(Admin, username=username)

        if not admin.check_password(password):
            return Response({
                "status": "false", 
                "message": "Invalid credentials", 
                "statusCode": "001"
                }, status=status.HTTP_401_UNAUTHORIZED)

        # request.session["admin_id"] = admin.id
        # request.session.modified = True
        admin_username = request.headers.get("username")
        return Response({
            "status": "true",
            "message": "Login successful",
            "statusCode": "000"
        }, status=status.HTTP_200_OK)

class AdminListCreateView(generics.ListCreateAPIView):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():

            password = serializer.validated_data.get("password")
            hashed_password = make_password(password)
            serializer.save(password=hashed_password)
            
            return Response({
                "status": "true",
                "message": "Admin created successfully",
                "statusCode": "000",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "false",
            "message": "Admin creation failed",
            "statusCode": "001",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class AdminLogoutView(APIView):
    def post(self, request):
        if "admin_id" in request.session:
            logout(request)
            return Response({
                "status": "true", 
                "message": "Logout successful", 
                "statusCode": "000"
                }, status=status.HTTP_200_OK)
        return Response({
            "status":"false",
            "message": "Already logged out", 
            "statusCode": "001"
            }, status=status.HTTP_400_BAD_REQUEST)

class LandingPageAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Fetch all banners
        banners = Banner.objects.all()
        banner_serializer = BannerSerializer(banners, many=True)

        # Fetch latest 4 trending products
        trending_products = Product.objects.filter(is_trending=True).order_by('-id')[:4]
        trending_products_serializer = ProductSerializer(trending_products, many=True)

        # Fetch latest 7 new arrival products
        new_arrival_products = Product.objects.filter(is_new_arrival=True).order_by('-id')[:7]
        new_arrival_products_serializer = ProductSerializer(new_arrival_products, many=True)

        # Fetch latest 4 subcategories for men
        men_subcategories = SubCategory.objects.filter(is_men=True).order_by('-id')[:4]
        men_subcategories_serializer = SubCategorySerializer(men_subcategories, many=True)

        # Fetch latest 4 subcategories for women
        women_subcategories = SubCategory.objects.filter(is_women=True).order_by('-id')[:4]
        women_subcategories_serializer = SubCategorySerializer(women_subcategories, many=True)

        # Fetch latest 4 subcategories for kids
        kids_subcategories = SubCategory.objects.filter(is_kids=True).order_by('-id')[:4]
        kids_subcategories_serializer = SubCategorySerializer(kids_subcategories, many=True)

        # Fetch video link
        video_link = Video.objects.all()
        video_link_serializer = VideoSerializer(video_link, many=True)

        response_data = {
            "status": "true",
            "message": "Landing page data retrieved successfully",
            "statusCode": "000",
            "data": {
                "banners": banner_serializer.data,
                "trending_products": trending_products_serializer.data,
                "new_arrival_products": new_arrival_products_serializer.data,
                "men_subcategories": men_subcategories_serializer.data,
                "women_subcategories": women_subcategories_serializer.data,
                "kids_subcategories": kids_subcategories_serializer.data,
                "video_link": video_link_serializer.data
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 50

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = CustomPagination

    def get_paginated_response(self, data):
        return Response({
            "status": "true",
            "message": "Products retrieved successfully",
            "statusCode": "000",
            "data": {
                "count": self.paginator.page.paginator.count,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": data
            }
        }, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "true",
            "message": "Products retrieved successfully",
            "statusCode": "000",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @require_admin_authentication
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                "status": "true",
                "message": "Product created successfully",
                "statusCode": "000",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Product creation failed",
            "statusCode": "001",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "true",
            "message": "Product retrieved successfully",
            "statusCode": "000",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @require_admin_authentication
    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "true",
                "message": "Product updated successfully",
                "statusCode": "000",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "false",
            "message": "Product update failed",
            "statusCode": "001",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @require_admin_authentication
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        instance.delete()
        return Response({
            "status": "true",
            "message": "Product deleted successfully",
            "statusCode": "000"
        }, status=status.HTTP_204_NO_CONTENT)


class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['type']

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        is_men = request.query_params.get('is_men', None)
        is_women = request.query_params.get('is_women', None)
        is_kids = request.query_params.get('is_kids', None)

        if is_men is not None:
            queryset = queryset.filter(is_men=is_men.lower() == 'true')

        if is_women is not None:
            queryset = queryset.filter(is_women=is_women.lower() == 'true')

        if is_kids is not None:
            queryset = queryset.filter(is_kids=is_kids.lower() == 'true')

        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "true",
            "message": "Subcategories retrieved successfully",
            "statusCode": "000",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @require_admin_authentication
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            subcategory = serializer.save()
            return Response({
                "status": "true",
                "message": "Subcategory created successfully",
                "statusCode": "000",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Subcategory creation failed",
            "statusCode": "001",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "true",
            "message": "Subcategory retrieved successfully",
            "statusCode": "000",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @require_admin_authentication
    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "true",
                "message": "Subcategory updated successfully",
                "statusCode": "000",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Subcategory update failed",
            "statusCode": "001",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @require_admin_authentication
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        instance.delete()
        return Response({
            "status": "true",
            "message": "Subcategory deleted successfully",
            "statusCode": "000"
        }, status=status.HTTP_204_NO_CONTENT)
    
class BannerListCreateView(generics.ListCreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "status": "true",
            "message": "Banners retrieved successfully",
            "statusCode": "000",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @require_admin_authentication
    def create(self, request, *args, **kwargs):

        if Banner.objects.count() >= 3:
            return Response({
                "status": "error",
                "message": "Only 3 banner images are allowed",
                "statusCode": "001"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                banner = serializer.save()
                return Response({
                    "status": "true",
                    "message": "Banner created successfully",
                    "statusCode": "000",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Database error",
                    "statusCode": "003",
                    "error_detail": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "error",
            "message": "Banner creation failed",
            "statusCode": "002",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class BannerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    @require_admin_authentication
    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            try:
                banner = serializer.save()
                return Response({
                    "status": "true",
                    "message": "Banner updated successfully",
                    "statusCode": "000",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Database error",
                    "statusCode": "003",
                    "error_detail": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "error",
            "message": "Banner update failed",
            "statusCode": "002",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @require_admin_authentication
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "status": "true",
            "message": "Banner deleted successfully",
            "statusCode": "000"
        }, status=status.HTTP_200_OK)

class VideoListCreateView(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            "status": "true",
            "message": "Video retrieved successfully",
            "statusCode": "000",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @require_admin_authentication
    def create(self, request, *args, **kwargs):

        existing_video = Video.objects.first()
        if existing_video:
            existing_video.delete()

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                video = serializer.save()
                return Response({
                    "status": "true",
                    "message": "Video link added successfully",
                    "statusCode": "000",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Database error",
                    "statusCode": "003",
                    "error_detail": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "error",
            "message": "Video link creation failed",
            "statusCode": "002",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    @require_admin_authentication
    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        instance.delete()

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                video = serializer.save()
                return Response({
                    "status": "true",
                    "message": "Video link updated successfully",
                    "statusCode": "000",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": "Database error",
                    "statusCode": "003",
                    "error_detail": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "error",
            "message": "Video link update failed",
            "statusCode": "002",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @require_admin_authentication
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "status": "true",
            "message": "Video link deleted successfully",
            "statusCode": "000"
        }, status=status.HTTP_200_OK)

