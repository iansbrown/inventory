# -*- coding: utf-8 -*-
"""
Camera capture API endpoint for equipment images.

Allows authenticated staff users to capture photos from device cameras
and save them as EquipmentImage records.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from equipment.models import EquipmentItem, EquipmentImage
import uuid
import base64
import logging

logger = logging.getLogger(__name__)


def is_staff_user(user):
    """Check if user is staff and can edit equipment."""
    return user.is_staff


@require_http_methods(["POST"])
@csrf_protect
@login_required(login_url="admin:login")
@user_passes_test(is_staff_user)
def capture_image(request, equipment_id):
    """
    Receive camera-captured image and save to EquipmentImage.
    
    POST Parameters:
    - image: Base64-encoded image data or blob (required)
    - image_type: Image category - 'condition', 'storage', 'setup', 'move', 'other' (optional, default='other')
    - caption: User-provided description (optional)
    - date_taken: ISO date string YYYY-MM-DD (optional)
    
    Returns:
    - JSON response with image_id, image_url, preview_url on success
    - JSON error response on failure
    """
    try:
        # Verify equipment exists
        try:
            equipment = EquipmentItem.objects.get(id=equipment_id)
        except EquipmentItem.DoesNotExist:
            logger.warning(f"Equipment not found: {equipment_id}")
            return JsonResponse(
                {"error": "Equipment not found"},
                status=404
            )
        
        # Extract image data from POST
        image_data = request.POST.get('image') or request.FILES.get('image')
        image_type = request.POST.get('image_type', 'other')
        caption = request.POST.get('caption', '')
        date_taken = request.POST.get('date_taken', None)
        
        # Validate image data
        if not image_data:
            logger.warning(f"No image provided for equipment {equipment_id}")
            return JsonResponse(
                {"error": "No image provided"},
                status=400
            )
        
        # Validate image type
        valid_types = [choice[0] for choice in EquipmentImage.IMAGE_TYPE_CHOICES]
        if image_type not in valid_types:
            image_type = 'other'
        
        # Handle base64 encoded string (from canvas)
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                # Extract base64 portion after comma
                try:
                    _, image_data_b64 = image_data.split(',', 1)
                    image_bytes = base64.b64decode(image_data_b64)
                except (ValueError, TypeError) as e:
                    logger.error(f"Failed to decode base64: {str(e)}")
                    return JsonResponse(
                        {"error": "Invalid image format"},
                        status=400
                    )
            else:
                # Assume it's already base64
                try:
                    image_bytes = base64.b64decode(image_data)
                except TypeError as e:
                    logger.error(f"Failed to decode base64: {str(e)}")
                    return JsonResponse(
                        {"error": "Invalid image format"},
                        status=400
                    )
        else:
            # Handle file upload (file object)
            image_bytes = image_data.read()
        
        # Validate image size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            logger.warning(f"Image too large: {len(image_bytes)} bytes")
            return JsonResponse(
                {"error": f"Image too large. Maximum size is 10MB."},
                status=400
            )
        
        # Validate minimum size (must be at least 100 bytes)
        if len(image_bytes) < 100:
            logger.warning(f"Image too small: {len(image_bytes)} bytes")
            return JsonResponse(
                {"error": "Image too small or empty"},
                status=400
            )
        
        # Create file object
        filename = f"camera_capture_{uuid.uuid4()}.jpg"
        image_file = ContentFile(image_bytes, name=filename)
        
        # Create EquipmentImage record
        eq_image = EquipmentImage.objects.create(
            equipment=equipment,
            image=image_file,
            image_type=image_type,
            caption=caption,
            date_taken=date_taken if date_taken else None
        )
        
        logger.info(
            f"Image captured: {eq_image.id} for equipment {equipment_id} "
            f"by user {request.user.username}"
        )
        
        return JsonResponse({
            "success": True,
            "image_id": eq_image.id,
            "image_url": eq_image.image.url,
            "preview_url": eq_image.image.url,
            "message": "Photo saved successfully"
        })
    
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JsonResponse(
            {"error": f"Validation error: {str(e)}"},
            status=400
        )
    except Exception as e:
        logger.error(f"Unexpected error in capture_image: {str(e)}")
        return JsonResponse(
            {"error": f"Failed to save image: {str(e)}"},
            status=500
        )
