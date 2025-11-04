"""
Resemblyzer utilities for voice embedding and similarity calculation.
Handles audio conversion, embedding generation, and cosine similarity computation.
"""

import os
import logging
from pathlib import Path

from typing import List, Tuple, Optional
import numpy as np
from pydub import AudioSegment
from resemblyzer import preprocess_wav, VoiceEncoder
from scipy.spatial.distance import cosine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResemblyzerUtils:
    """Utility class for voice embedding and similarity operations."""
    
    def __init__(self):
        """Initialize ResemblyzerUtils with voice encoder."""
        self.encoder = VoiceEncoder()
        logger.info("Voice encoder initialized")
    
    def convert_to_wav(
        self, 
        input_path: str, 
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> bool:
        """
        Convert any audio format to WAV format.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output WAV file
            sample_rate: Target sample rate (default: 16000 Hz)
            channels: Number of audio channels (default: 1 for mono)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                logger.error(f"Input file not found: {input_path}")
                return False
            
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Set properties
            audio = audio.set_channels(channels)
            audio = audio.set_frame_rate(sample_rate)
            
            # Export as WAV
            audio.export(output_path, format='wav')
            
            logger.info(f"Converted to WAV: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting to WAV: {e}")
            return False
    
    def generate_embedding(
        self, 
        wav_path: str, 
        output_path: Optional[str] = None
    ) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Generate voice embedding using Resemblyzer.
        
        Args:
            wav_path: Path to WAV audio file
            output_path: Optional path to save embedding (as .npy file)
            
        Returns:
            Tuple of (success: bool, embedding: np.ndarray or None)
        """
        try:
            # Check if WAV file exists
            if not os.path.exists(wav_path):
                logger.error(f"WAV file not found: {wav_path}")
                return False, None
            
            # Preprocess audio
            wav = preprocess_wav(wav_path)
            
            # Generate embedding
            embedding = self.encoder.embed_utterance(wav)
            
            # Save embedding if output path provided
            if output_path:
                np.save(output_path, embedding)
                logger.info(f"Embedding saved: {output_path}")
            
            logger.info(f"Generated embedding for: {wav_path}")
            return True, embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return False, None
    
    def store_embedding_locally(
        self, 
        embedding: np.ndarray, 
        output_path: str
    ) -> bool:
        """
        Store embedding in local storage.
        
        Args:
            embedding: Numpy array containing the embedding
            output_path: Path to save the embedding file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save embedding
            np.save(output_path, embedding)
            
            logger.info(f"Embedding stored: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return False
    
    def calculate_cosine_similarity(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity score (0 to 1, higher is more similar)
        """
        try:
            # Cosine similarity = 1 - cosine distance
            similarity = 1 - cosine(embedding1, embedding2)
            
            logger.debug(f"Cosine similarity: {similarity:.4f}")
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def calculate_mean_similarity(
        self, 
        sample_embedding: np.ndarray, 
        stored_embeddings_dir: str = 'embeddings'
    ) -> Tuple[float, List[float]]:
        """
        Calculate mean cosine similarity with all stored embeddings.
        
        Args:
            sample_embedding: Embedding of the sample audio
            stored_embeddings_dir: Directory containing stored embeddings
            
        Returns:
            Tuple of (mean_similarity: float, all_similarities: List[float])
        """
        try:
            similarities = []
            
            # Check if directory exists
            if not os.path.exists(stored_embeddings_dir):
                logger.error(f"Embeddings directory not found: {stored_embeddings_dir}")
                return 0.0, []
            
            # Get all .npy files
            embedding_files = [
                f for f in os.listdir(stored_embeddings_dir) 
                if f.endswith('.npy')
            ]
            
            if not embedding_files:
                logger.warning(f"No embeddings found in: {stored_embeddings_dir}")
                return 0.0, []
            
            # Calculate similarity with each stored embedding
            for embedding_file in embedding_files:
                embedding_path = os.path.join(stored_embeddings_dir, embedding_file)
                
                try:
                    stored_embedding = np.load(embedding_path)
                    similarity = self.calculate_cosine_similarity(
                        sample_embedding, 
                        stored_embedding
                    )
                    similarities.append(similarity)
                    
                except Exception as e:
                    logger.warning(f"Error loading {embedding_file}: {e}")
                    continue
            
            # Calculate mean
            if similarities:
                mean_similarity = np.mean(similarities)
                logger.info(
                    f"Mean similarity: {mean_similarity:.4f} "
                    f"(from {len(similarities)} embeddings)"
                )
                return float(mean_similarity), similarities
            else:
                logger.warning("No valid similarities calculated")
                return 0.0, []
            
        except Exception as e:
            logger.error(f"Error calculating mean similarity: {e}")
            return 0.0, []
    
    def process_audio_to_embedding(
        self, 
        audio_path: str, 
        output_dir: str = 'sample_embedding'
    ) -> Tuple[bool, Optional[np.ndarray], Optional[str]]:
        """
        Complete pipeline: convert audio to WAV, generate embedding, and store it.
        
        Args:
            audio_path: Path to input audio file
            output_dir: Directory to save the embedding
            
        Returns:
            Tuple of (success: bool, embedding: np.ndarray or None, embedding_path: str or None)
        """
        wav_path = None
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Get base filename
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            # Convert to WAV
            wav_path = os.path.join('sample', f"{base_name}.wav")
            os.makedirs('sample', exist_ok=True)
            
            if not self.convert_to_wav(audio_path, wav_path):
                return False, None, None
            
            # Generate embedding
            embedding_path = os.path.join(output_dir, f"{base_name}_embedding.npy")
            success, embedding = self.generate_embedding(wav_path, embedding_path)
            
            if not success:
                return False, None, None
            
            logger.info(f"Successfully processed audio to embedding: {audio_path}")
            return True, embedding, embedding_path
            
        except Exception as e:
            logger.error(f"Error in audio processing pipeline: {e}")
            return False, None, None
        
        finally:
            # Clean up WAV file if it exists
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                    logger.debug(f"Cleaned up WAV file: {wav_path}")
                except Exception as e:
                    logger.warning(f"Could not remove WAV file: {e}")


# Convenience functions for direct usage
def convert_audio(input_path: str, output_path: str) -> bool:
    """Convert audio to WAV format."""
    utils = ResemblyzerUtils()
    return utils.convert_to_wav(input_path, output_path)


def embed_audio(wav_path: str, output_path: str = None) -> Tuple[bool, Optional[np.ndarray]]:
    """Generate embedding from WAV audio."""
    utils = ResemblyzerUtils()
    return utils.generate_embedding(wav_path, output_path)


def compare_embeddings(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """Calculate cosine similarity between embeddings."""
    utils = ResemblyzerUtils()
    return utils.calculate_cosine_similarity(embedding1, embedding2)


def get_mean_similarity(sample_embedding: np.ndarray, embeddings_dir: str = 'embeddings') -> float:
    """Calculate mean similarity with stored embeddings."""
    utils = ResemblyzerUtils()
    mean_sim, _ = utils.calculate_mean_similarity(sample_embedding, embeddings_dir)
    return mean_sim


if __name__ == "__main__":
    # Test the functionality
    logger.info("Testing Resemblyzer utilities...")
    utils = ResemblyzerUtils()
    logger.info("✓ Resemblyzer utilities initialized successfully")