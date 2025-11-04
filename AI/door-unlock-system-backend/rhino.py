"""
Rhino utilities for intent recognition from audio.
Handles speech-to-intent processing using Picovoice Rhino.
"""

import os
import logging
from typing import Dict, Optional
import pvrhino
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rhino configuration
RHINO_ACCESS_KEY = os.getenv("RHINO_ACCESS_KEY")
RHINO_CONTEXT_PATH = os.getenv("RHINO_CONTEXT_PATH")


class RhinoUtils:
    """Utility class for intent recognition using Picovoice Rhino."""
    
    def __init__(
        self, 
        access_key: str = RHINO_ACCESS_KEY,
        context_path: str = RHINO_CONTEXT_PATH
    ):
        """
        Initialize RhinoUtils with Rhino engine.
        
        Args:
            access_key: Picovoice access key
            context_path: Path to Rhino context file (.rhn)
        """
        self.access_key = access_key
        self.context_path = context_path
        self.rhino = None
        
        try:
            self.rhino = pvrhino.create(
                access_key=access_key,
                context_path=context_path
            )
            logger.info("Rhino engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Rhino: {e}")
            logger.error("Please check your access key and context path")
    
    def process_audio(
        self, 
        wav_path: str
    ) -> Dict[str, any]:
        """
        Process WAV audio file and extract intent and slots.
        
        Args:
            wav_path: Path to WAV audio file (16kHz, mono, 16-bit)
            
        Returns:
            Dict containing:
                - is_understood: bool
                - intent: str or None
                - slots: dict or None
                - error: str or None
        """
        result = {
            'is_understood': False,
            'intent': None,
            'slots': None,
            'error': None
        }
        
        try:
            if self.rhino is None:
                result['error'] = "Rhino engine not initialized"
                logger.error(result['error'])
                return result
            
            # Check if file exists
            if not os.path.exists(wav_path):
                result['error'] = f"Audio file not found: {wav_path}"
                logger.error(result['error'])
                return result
            
            # Read audio file
            import wave
            import struct
            
            with wave.open(wav_path, 'rb') as wav_file:
                # Validate audio format
                if wav_file.getnchannels() != 1:
                    result['error'] = "Audio must be mono (single channel)"
                    logger.error(result['error'])
                    return result
                
                if wav_file.getframerate() != self.rhino.sample_rate:
                    result['error'] = f"Audio sample rate must be {self.rhino.sample_rate} Hz"
                    logger.error(result['error'])
                    return result
                
                if wav_file.getsampwidth() != 2:
                    result['error'] = "Audio must be 16-bit"
                    logger.error(result['error'])
                    return result
                
                # Read audio frames
                num_frames = wav_file.getnframes()
                audio_data = wav_file.readframes(num_frames)
                
                # Convert to 16-bit integers
                audio_samples = struct.unpack(
                    f'{num_frames}h', 
                    audio_data
                )
            
            # Process audio with Rhino
            frame_length = self.rhino.frame_length
            
            for i in range(0, len(audio_samples), frame_length):
                frame = audio_samples[i:i + frame_length]
                
                # Pad the last frame if necessary
                if len(frame) < frame_length:
                    frame = list(frame) + [0] * (frame_length - len(frame))
                
                is_finalized = self.rhino.process(frame)
                
                if is_finalized:
                    inference = self.rhino.get_inference()
                    
                    result['is_understood'] = inference.is_understood
                    
                    if inference.is_understood:
                        result['intent'] = inference.intent
                        result['slots'] = inference.slots
                        
                        logger.info(f"Intent detected: {inference.intent}")
                        logger.info(f"Slots: {inference.slots}")
                    else:
                        logger.info("Speech not understood")
                    
                    # Reset Rhino for next inference
                    self.rhino.reset()
                    break
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing audio with Rhino: {e}")
            return result
    
    def get_context_info(self) -> Optional[str]:
        """
        Get information about the loaded Rhino context.
        
        Returns:
            str: Context information or None if not available
        """
        try:
            if self.rhino is None:
                return None
            
            return self.rhino.context_info
            
        except Exception as e:
            logger.error(f"Error getting context info: {e}")
            return None
    
    def cleanup(self):
        """Clean up Rhino resources."""
        try:
            if self.rhino is not None:
                self.rhino.delete()
                logger.info("Rhino engine cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


def process_wav_for_intent(wav_path: str) -> Dict[str, any]:
    """
    Convenience function to process WAV file and get intent.
    
    Args:
        wav_path: Path to WAV audio file
        
    Returns:
        Dict containing intent recognition results
    """
    rhino = RhinoUtils()
    result = rhino.process_audio(wav_path)
    rhino.cleanup()
    return result


if __name__ == "__main__":
    # Test the functionality
    logger.info("Testing Rhino utilities...")
    
    # Check if access key and context are set
    if RHINO_ACCESS_KEY == "your-picovoice-access-key":
        logger.warning("Please set RHINO_ACCESS_KEY environment variable")
    
    if RHINO_CONTEXT_PATH == "path/to/context.rhn":
        logger.warning("Please set RHINO_CONTEXT_PATH environment variable")
    
    # Create instance
    try:
        rhino = RhinoUtils()
        context_info = rhino.get_context_info()
        
        if context_info:
            logger.info(f"Context info:\n{context_info}")
        
        logger.info("✓ Rhino utilities initialized successfully")
        rhino.cleanup()
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize Rhino: {e}")