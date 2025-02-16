from rest_framework import serializers
from .models import Admin, Product, SubCategory, Banner, Video
from django.core.files.base import ContentFile
import base64

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ["id", "admin_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

class ProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    class Meta:
        model = Product
        fields = '__all__'

    def validate_images(self, images):
        
        if len(images) > 3:
            raise serializers.ValidationError("You can upload a maximum of 3 images.")

        for img in images:
            try:
                base64.b64decode(img.split(';base64,')[-1])
            except Exception:
                raise serializers.ValidationError("Invalid base64 image format.")

        return images

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)  
        product.images = images
        product.save()
        return product


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = SubCategory
        fields = '__all__'

    def validate_image(self, image):

        if image:
            try:
                base64.b64decode(image.split(';base64,')[-1])
            except Exception:
                raise serializers.ValidationError("Invalid base64 image format.")
        return image

    def create(self, validated_data):
        image = validated_data.get('image', None)
        subcategory = SubCategory.objects.create(**validated_data)
        subcategory.image = image
        subcategory.save()
        return subcategory
    
class BannerSerializer(serializers.ModelSerializer):
    image = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Banner
        fields = '__all__'

    def validate_image(self, image):

        if image:
            try:
                base64.b64decode(image.split(';base64,')[-1])
            except Exception:
                raise serializers.ValidationError("Invalid base64 image format.")
        return image

    def create(self, validated_data):
        """Check max banner limit and create new banner."""
        if Banner.objects.count() >= 3:
            raise serializers.ValidationError("Only 3 banner images are allowed.")
        
        return Banner.objects.create(**validated_data)

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
