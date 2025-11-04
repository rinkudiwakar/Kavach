"""
Main pipeline for audio-based door unlock system.
Orchestrates voice recognition, embedding comparison, and intent detection.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Tuple, Optional
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from resemblyzer_utils import ResemblyzerUtils
from rhino import RhinoUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.75"))
EMBEDDINGS_DIR = "embeddings"
SAMPLE_DIR = "sample"
SAMPLE_EMBEDDING_DIR = "sample_embedding"


class DoorUnlockPipeline:
    """Main pipeline for audio-based door unlock system."""
    
    def __init__(
        self, 
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        embeddings_dir: str = EMBEDDINGS_DIR
    ):
        """
        Initialize the door unlock pipeline.
        
        Args:
            similarity_threshold: Minimum similarity score for voice match
            embeddings_dir: Directory containing stored voice embeddings
        """
        self.similarity_threshold = similarity_threshold
        self.embeddings_dir = embeddings_dir
        
        # Initialize utilities
        self.resemblyzer = ResemblyzerUtils()
        self.rhino = RhinoUtils()
        
        # Setup directories
        self._setup_directories()
        
        logger.info(f"Pipeline initialized with threshold: {similarity_threshold}")
    
    def _setup_directories(self):
        """Create necessary directories."""
        directories = [SAMPLE_DIR, SAMPLE_EMBEDDING_DIR, self.embeddings_dir]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def process_new_audio(
        self, 
        audio_path: str
    ) -> Tuple[Optional[np.ndarray], Optional[str], Optional[str]]:
        """
        Process new audio: convert to WAV and generate embedding.
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Tuple of (embedding, wav_path, embedding_path)
        """
        try:
            # Get base filename
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            
            # Convert to WAV
            wav_path = os.path.join(SAMPLE_DIR, f"{base_name}.wav")
            if not self.resemblyzer.convert_to_wav(audio_path, wav_path):
                logger.error("Failed to convert audio to WAV")
                return None, None, None
            
            # Generate embedding
            embedding_path = os.path.join(
                SAMPLE_EMBEDDING_DIR, 
                f"{base_name}_embedding.npy"
            )
            success, embedding = self.resemblyzer.generate_embedding(
                wav_path, 
                embedding_path
            )
            
            if not success:
                logger.error("Failed to generate embedding")
                return None, wav_path, None
            
            logger.info("Audio processed successfully")
            return embedding, wav_path, embedding_path
            
        except Exception as e:
            logger.error(f"Error processing new audio: {e}")
            return None, None, None
    
    def calculate_voice_similarity(
        self, 
        sample_embedding: np.ndarray
    ) -> Tuple[float, list]:
        """
        Calculate cosine similarity with all stored embeddings.
        
        Args:
            sample_embedding: Embedding of the sample audio
            
        Returns:
            Tuple of (mean_similarity, all_similarities)
        """
        try:
            mean_sim, all_sims = self.resemblyzer.calculate_mean_similarity(
                sample_embedding,
                self.embeddings_dir
            )
            
            logger.info(f"Voice similarity score: {mean_sim:.4f}")
            return mean_sim, all_sims
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0, []
    
    def recognize_intent(self, wav_path: str) -> Dict[str, any]:
        """
        Recognize intent from WAV audio using Rhino.
        
        Args:
            wav_path: Path to WAV audio file
            
        Returns:
            Dict containing intent recognition results
        """
        try:
            result = self.rhino.process_audio(wav_path)
            
            if result.get('error'):
                logger.error(f"Rhino error: {result['error']}")
            elif result['is_understood']:
                logger.info(f"Intent recognized: {result['intent']}")
            else:
                logger.info("Intent not understood")
            
            return result
            
        except Exception as e:
            logger.error(f"Error recognizing intent: {e}")
            return {
                'is_understood': False,
                'intent': None,
                'slots': None,
                'error': str(e)
            }
    
    def process_parallel(
        self, 
        wav_path: str, 
        sample_embedding: np.ndarray
    ) -> Tuple[float, Dict[str, any]]:
        """
        Process similarity and intent recognition in parallel.
        
        Args:
            wav_path: Path to WAV audio file
            sample_embedding: Embedding of the sample audio
            
        Returns:
            Tuple of (mean_similarity, intent_result)
        """
        mean_similarity = 0.0
        intent_result = {}
        
        try:
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit both tasks
                similarity_future = executor.submit(
                    self.calculate_voice_similarity, 
                    sample_embedding
                )
                intent_future = executor.submit(
                    self.recognize_intent, 
                    wav_path
                )
                
                # Wait for both to complete
                for future in as_completed([similarity_future, intent_future]):
                    if future == similarity_future:
                        mean_similarity, _ = future.result()
                    elif future == intent_future:
                        intent_result = future.result()
            
            return mean_similarity, intent_result
            
        except Exception as e:
            logger.error(f"Error in parallel processing: {e}")
            return 0.0, {
                'is_understood': False,
                'intent': None,
                'slots': None,
                'error': str(e)
            }
    
    def make_decision(
        self, 
        similarity_score: float, 
        intent_result: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Make final decision based on similarity and intent.
        
        Args:
            similarity_score: Voice similarity score
            intent_result: Intent recognition result
            
        Returns:
            Dict containing:
                - action: str (open, locked, rejected, invalid)
                - message: str
                - similarity_score: float
                - intent: str or None
        """
        decision = {
            'action': 'invalid',
            'message': 'Unknown error',
            'similarity_score': similarity_score,
            'intent': intent_result.get('intent')
        }
        
        try:
            # Check if intent was understood
            if not intent_result.get('is_understood'):
                decision['action'] = 'invalid'
                decision['message'] = 'Please say the correct keyword'
                logger.warning("Intent not understood")
                return decision
            
            intent = intent_result.get('intent')
            
            # Check similarity threshold
            if similarity_score < self.similarity_threshold:
                decision['action'] = 'rejected'
                decision['message'] = f'Voice does not match (score: {similarity_score:.2f})'
                logger.warning(f"Voice rejected: {similarity_score:.2f} < {self.similarity_threshold}")
                return decision
            
            # Process based on intent
            if intent == 'unlock_door':
                decision['action'] = 'open'
                decision['message'] = f'Door is open! (score: {similarity_score:.2f})'
                logger.info(f"✓ Door unlocked for authorized user")
                
            elif intent == 'lock_door':
                decision['action'] = 'locked'
                decision['message'] = f'Door is locked (score: {similarity_score:.2f})'
                logger.info(f"✓ Door locked by authorized user")
                
            else:
                decision['action'] = 'invalid'
                decision['message'] = f'Unknown command: {intent}'
                logger.warning(f"Unknown intent: {intent}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error making decision: {e}")
            decision['message'] = f'Error: {str(e)}'
            return decision
    
    def cleanup_temp_files(
        self, 
        wav_path: Optional[str], 
        embedding_path: Optional[str]
    ):
        """
        Clean up temporary audio and embedding files.
        
        Args:
            wav_path: Path to WAV file
            embedding_path: Path to embedding file
        """
        try:
            files_to_delete = [wav_path, embedding_path]
            
            for file_path in files_to_delete:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted: {file_path}")
            
            logger.info("Temporary files cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
    
    def execute(self, audio_path: str) -> Dict[str, any]:
        """
        Execute the complete pipeline for door unlock decision.
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Dict containing the final decision
        """
        wav_path = None
        embedding_path = None
        
        try:
            logger.info(f"Processing audio: {audio_path}")
            
            # Step 1: Process new audio
            embedding, wav_path, embedding_path = self.process_new_audio(audio_path)
            
            if embedding is None or wav_path is None:
                return {
                    'action': 'error',
                    'message': 'Failed to process audio',
                    'similarity_score': 0.0,
                    'intent': None
                }
            
            # Step 2 & 3: Calculate similarity and recognize intent (parallel)
            similarity_score, intent_result = self.process_parallel(
                wav_path, 
                embedding
            )
            
            # Step 4: Make decision
            decision = self.make_decision(similarity_score, intent_result)
            
            logger.info(f"Final decision: {decision['action']} - {decision['message']}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            return {
                'action': 'error',
                'message': f'Pipeline error: {str(e)}',
                'similarity_score': 0.0,
                'intent': None
            }
        
        finally:
            # Step 5: Cleanup
            self.cleanup_temp_files(wav_path, embedding_path)
    
    def shutdown(self):
        """Clean up resources."""
        try:
            if self.rhino:
                self.rhino.cleanup()
            logger.info("Pipeline shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def process_audio(audio_path: str, threshold: float = SIMILARITY_THRESHOLD) -> Dict[str, any]:
    """
    Convenience function to process a single audio file.
    
    Args:
        audio_path: Path to input audio file
        threshold: Similarity threshold for voice matching
        
    Returns:
        Dict containing the decision
    """
    pipeline = DoorUnlockPipeline(similarity_threshold=threshold)
    result = pipeline.execute(audio_path)
    pipeline.shutdown()
    return result


if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    # if len(sys.argv) < 2:
    #     logger.error("Usage: python main_pipeline.py")
    #     sys.exit(1)
    
    #audio_file = sys.argv[1]
    audio_file="temp_audio/test audio.aac"
    
    # Check if file exists
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        sys.exit(1)
    
    # Process audio
    logger.info("=" * 60)
    logger.info("DOOR UNLOCK SYSTEM - AUDIO PROCESSING")
    logger.info("=" * 60)
    
    result = process_audio(audio_file)
    
    # Display result
    logger.info("=" * 60)
    logger.info("RESULT:")
    logger.info(f"  Action: {result['action'].upper()}")
    logger.info(f"  Message: {result['message']}")
    logger.info(f"  Similarity Score: {result['similarity_score']:.4f}")
    logger.info(f"  Intent: {result['intent']}")
    logger.info("=" * 60)