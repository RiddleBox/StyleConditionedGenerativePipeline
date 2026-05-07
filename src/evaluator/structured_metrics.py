"""
Structured Style Metrics Evaluator

Implements 6 style dimensions according to the three-way mapping table:
1. color: K-means + Wasserstein distance
2. line: Canny edge detection
3. lighting: Brightness histogram distance
4. composition: CLIP spatial features
5. material: Gabor filters (texture)
6. detail_density: High-frequency components
"""

import cv2
import numpy as np
from PIL import Image
from typing import Union, Dict, Tuple
from scipy.stats import wasserstein_distance
from scipy.spatial.distance import cosine
from sklearn.cluster import KMeans


class StructuredMetrics:
    """
    Structured style metrics evaluator.
    
    Computes 6 dimensional style scores based on image analysis.
    All metrics are deterministic (same input → same output ±0.02).
    """
    
    def __init__(self):
        """Initialize structured metrics evaluator"""
        pass
    
    def evaluate(
        self,
        reference_image: Union[str, Image.Image, np.ndarray],
        generated_image: Union[str, Image.Image, np.ndarray]
    ) -> Dict[str, float]:
        """
        Evaluate all 6 style dimensions.
        
        Args:
            reference_image: Reference image
            generated_image: Generated image
        
        Returns:
            Dict with 6 scores: color, line, lighting, composition, material, detail_density
            Each score is in [0, 1] where 1 = perfect match
        """
        # Load images as numpy arrays
        ref_img = self._load_image(reference_image)
        gen_img = self._load_image(generated_image)
        
        # Resize to same size for fair comparison
        target_size = (512, 512)
        ref_img = cv2.resize(ref_img, target_size)
        gen_img = cv2.resize(gen_img, target_size)
        
        # Compute all metrics
        scores = {
            'color': self._evaluate_color(ref_img, gen_img),
            'line': self._evaluate_line(ref_img, gen_img),
            'lighting': self._evaluate_lighting(ref_img, gen_img),
            'composition': self._evaluate_composition(ref_img, gen_img),
            'material': self._evaluate_material(ref_img, gen_img),
            'detail_density': self._evaluate_detail_density(ref_img, gen_img)
        }
        
        return scores
    
    def _load_image(self, image: Union[str, Image.Image, np.ndarray]) -> np.ndarray:
        """Load image as RGB numpy array"""
        if isinstance(image, str):
            img = Image.open(image).convert("RGB")
            return np.array(img)
        elif isinstance(image, Image.Image):
            return np.array(image.convert("RGB"))
        elif isinstance(image, np.ndarray):
            if len(image.shape) == 2:  # Grayscale
                return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            return image
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
    
    def _evaluate_color(self, ref_img: np.ndarray, gen_img: np.ndarray) -> float:
        """
        Evaluate color similarity using K-means + Wasserstein distance.
        
        Steps:
        1. Extract dominant colors (K-means, k=5)
        2. Compute color distributions
        3. Wasserstein distance between distributions
        """
        # Extract dominant colors
        ref_colors = self._extract_dominant_colors(ref_img, k=5)
        gen_colors = self._extract_dominant_colors(gen_img, k=5)
        
        # Compute color histograms in LAB space
        ref_lab = cv2.cvtColor(ref_img, cv2.COLOR_RGB2LAB)
        gen_lab = cv2.cvtColor(gen_img, cv2.COLOR_RGB2LAB)
        
        # Compute Wasserstein distance for each channel
        distances = []
        for channel in range(3):
            ref_hist, _ = np.histogram(ref_lab[:, :, channel].flatten(), bins=256, range=(0, 256), density=True)
            gen_hist, _ = np.histogram(gen_lab[:, :, channel].flatten(), bins=256, range=(0, 256), density=True)
            dist = wasserstein_distance(ref_hist, gen_hist)
            distances.append(dist)
        
        # Average distance, normalize to [0, 1]
        avg_distance = np.mean(distances)
        # Wasserstein distance is typically in [0, ~0.5] for normalized histograms
        similarity = 1.0 - min(avg_distance * 2.0, 1.0)
        
        return float(similarity)
    
    def _extract_dominant_colors(self, img: np.ndarray, k: int = 5) -> np.ndarray:
        """Extract k dominant colors using K-means"""
        pixels = img.reshape(-1, 3).astype(np.float32)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        return kmeans.cluster_centers_
    
    def _evaluate_line(self, ref_img: np.ndarray, gen_img: np.ndarray) -> float:
        """
        Evaluate line similarity using Canny edge detection.
        
        Steps:
        1. Convert to grayscale
        2. Apply Canny edge detection
        3. Compare edge maps (IoU)
        """
        # Convert to grayscale
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_RGB2GRAY)
        gen_gray = cv2.cvtColor(gen_img, cv2.COLOR_RGB2GRAY)
        
        # Apply Canny edge detection
        ref_edges = cv2.Canny(ref_gray, 100, 200)
        gen_edges = cv2.Canny(gen_gray, 100, 200)
        
        # Compute IoU (Intersection over Union)
        intersection = np.logical_and(ref_edges, gen_edges).sum()
        union = np.logical_or(ref_edges, gen_edges).sum()
        
        if union == 0:
            return 1.0  # Both images have no edges
        
        iou = intersection / union
        return float(iou)
    
    def _evaluate_lighting(self, ref_img: np.ndarray, gen_img: np.ndarray) -> float:
        """
        Evaluate lighting similarity using brightness histogram distance.
        
        Steps:
        1. Convert to LAB, extract L channel (brightness)
        2. Compute histograms
        3. Chi-square distance
        """
        # Convert to LAB and extract L channel
        ref_lab = cv2.cvtColor(ref_img, cv2.COLOR_RGB2LAB)
        gen_lab = cv2.cvtColor(gen_img, cv2.COLOR_RGB2LAB)
        
        ref_l = ref_lab[:, :, 0]
        gen_l = gen_lab[:, :, 0]
        
        # Compute histograms
        ref_hist, _ = np.histogram(ref_l.flatten(), bins=256, range=(0, 256), density=True)
        gen_hist, _ = np.histogram(gen_l.flatten(), bins=256, range=(0, 256), density=True)
        
        # Chi-square distance
        chi_square = np.sum((ref_hist - gen_hist) ** 2 / (ref_hist + gen_hist + 1e-10))
        
        # Normalize to [0, 1]
        similarity = 1.0 - min(chi_square / 2.0, 1.0)
        
        return float(similarity)
    
    def _evaluate_composition(self, ref_img: np.ndarray, gen_img: np.ndarray) -> float:
        """
        Evaluate composition similarity using spatial features.
        
        Steps:
        1. Divide image into 3x3 grid
        2. Compute average color/brightness per cell
        3. Compare spatial distributions
        """
        # Divide into 3x3 grid
        ref_features = self._extract_spatial_features(ref_img, grid_size=3)
        gen_features = self._extract_spatial_features(gen_img, grid_size=3)
        
        # Compute cosine similarity
        similarity = 1.0 - cosine(ref_features.flatten(), gen_features.flatten())
        
        return float(max(0.0, similarity))
    
    def _extract_spatial_features(self, img: np.ndarray, grid_size: int = 3) -> np.ndarray:
        """Extract spatial features by dividing image into grid"""
        h, w = img.shape[:2]
        cell_h = h // grid_size
        cell_w = w // grid_size
        
        features = []
        for i in range(grid_size):
            for j in range(grid_size):
                cell = img[i*cell_h:(i+1)*cell_h, j*cell_w:(j+1)*cell_w]
                # Average color and brightness
                avg_color = cell.mean(axis=(0, 1))
                features.extend(avg_color)
        
        return np.array(features)
    
    def _evaluate_material(self, ref_img: np.ndarray, gen_img: np.ndarray) -> float:
        """
        Evaluate material/texture similarity using Gabor filters.
        
        Steps:
        1. Apply Gabor filters at multiple scales/orientations
        2. Compute texture features
        3. Compare feature vectors
        """
        # Convert to grayscale
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        gen_gray = cv2.cvtColor(gen_img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        
        # Extract Gabor features
        ref_features = self._extract_gabor_features(ref_gray)
        gen_features = self._extract_gabor_features(gen_gray)
        
        # Compute cosine similarity
        similarity = 1.0 - cosine(ref_features, gen_features)
        
        return float(max(0.0, similarity))
    
    def _extract_gabor_features(self, gray_img: np.ndarray) -> np.ndarray:
        """Extract Gabor texture features"""
        features = []
        
        # Multiple scales and orientations
        scales = [3, 5, 7]
        orientations = [0, 45, 90, 135]
        
        for scale in scales:
            for theta in orientations:
                # Create Gabor kernel
                kernel = cv2.getGaborKernel(
                    (scale*2+1, scale*2+1),
                    sigma=scale/2,
                    theta=np.deg2rad(theta),
                    lambd=scale,
                    gamma=0.5,
                    psi=0
                )
                
                # Apply filter
                filtered = cv2.filter2D(gray_img, cv2.CV_32F, kernel)
                
                # Compute mean and std as features
                features.append(filtered.mean())
                features.append(filtered.std())
        
        return np.array(features)
    
    def _evaluate_detail_density(self, ref_img: np.ndarray, gen_img: np.ndarray) -> float:
        """
        Evaluate detail density using high-frequency components.
        
        Steps:
        1. Apply Laplacian filter (high-pass)
        2. Compute variance of filtered image
        3. Compare variances
        """
        # Convert to grayscale
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_RGB2GRAY)
        gen_gray = cv2.cvtColor(gen_img, cv2.COLOR_RGB2GRAY)
        
        # Apply Laplacian
        ref_laplacian = cv2.Laplacian(ref_gray, cv2.CV_64F)
        gen_laplacian = cv2.Laplacian(gen_gray, cv2.CV_64F)
        
        # Compute variances
        ref_variance = ref_laplacian.var()
        gen_variance = gen_laplacian.var()
        
        # Compare variances (ratio)
        if ref_variance == 0 and gen_variance == 0:
            return 1.0
        
        ratio = min(ref_variance, gen_variance) / (max(ref_variance, gen_variance) + 1e-10)
        
        return float(ratio)
