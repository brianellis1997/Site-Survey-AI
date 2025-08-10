from typing import List, Tuple, Optional, Dict
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
import logging
from transformers import CLIPProcessor, CLIPModel

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_model = None
        self.embedding_processor = None
        
        # Standard image preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    async def initialize_embedding_model(self):
        """Initialize CLIP model for generating image embeddings"""
        if not self.embedding_model:
            logger.info("Loading CLIP model for image embeddings")
            self.embedding_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.embedding_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.embedding_model.to(self.device)
    
    async def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for analysis - resize, enhance contrast, etc."""
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        lab_planes = list(cv2.split(lab))
        
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab_planes[0] = clahe.apply(lab_planes[0])
        
        enhanced_lab = cv2.merge(lab_planes)
        enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        
        # Convert back to PIL Image
        enhanced_image = Image.fromarray(enhanced_rgb)
        
        # Ensure reasonable size (not too large, not too small)
        width, height = enhanced_image.size
        max_size = 1024
        
        if max(width, height) > max_size:
            ratio = max_size / max(width, height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            enhanced_image = enhanced_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return enhanced_image
    
    async def get_image_embedding(self, image: Image.Image) -> List[float]:
        """Generate embedding vector for the image using CLIP"""
        
        if not self.embedding_model:
            await self.initialize_embedding_model()
        
        # Preprocess image for CLIP
        inputs = self.embedding_processor(
            images=image,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            image_features = self.embedding_model.get_image_features(**inputs)
            # Normalize the features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        # Convert to list of floats for storage
        embedding = image_features.cpu().numpy().flatten().tolist()
        
        return embedding
    
    async def detect_components(self, image: Image.Image) -> List[Dict[str, any]]:
        """Basic component detection using contours and shape analysis"""
        
        # Convert to OpenCV format
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        components = []
        for i, contour in enumerate(contours):
            # Filter out very small contours
            area = cv2.contourArea(contour)
            if area < 100:  # Minimum area threshold
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Calculate component properties
            aspect_ratio = w / h
            extent = area / (w * h)
            
            # Basic shape classification
            shape_type = "unknown"
            if aspect_ratio > 0.8 and aspect_ratio < 1.2:
                shape_type = "circular_component"  # Could be bolt head, bearing, etc.
            elif aspect_ratio > 3:
                shape_type = "linear_component"    # Could be rod, pipe, etc.
            elif extent > 0.8:
                shape_type = "rectangular_component"
            
            components.append({
                "component_id": i,
                "bounding_box": (x, y, w, h),
                "area": area,
                "shape_type": shape_type,
                "aspect_ratio": aspect_ratio,
                "extent": extent
            })
        
        return components
    
    async def crop_component(
        self, 
        image: Image.Image, 
        bounding_box: Tuple[int, int, int, int],
        padding: int = 10
    ) -> Image.Image:
        """Crop a specific component from the image with padding"""
        
        x, y, w, h = bounding_box
        
        # Add padding
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.width - x, w + 2 * padding)
        h = min(image.height - y, h + 2 * padding)
        
        cropped = image.crop((x, y, x + w, y + h))
        return cropped
    
    async def batch_process_images(self, images: List[Image.Image]) -> List[Image.Image]:
        """Process multiple images in batch"""
        processed_images = []
        
        for image in images:
            processed_img = await self.preprocess_image(image)
            processed_images.append(processed_img)
        
        return processed_images