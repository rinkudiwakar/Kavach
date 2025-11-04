"""
Database utilities for audio file management and embedding storage.
Handles Supabase storage operations for audio files and embeddings.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
from supabase import create_client, Client
from resemblyzer import preprocess_wav, VoiceEncoder
from pydub import AudioSegment
from dotenv import load_dotenv
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
AUDIO_BUCKET = os.getenv("AUDIO_BUCKET", "voice_samples")
EMBEDDING_BUCKET = os.getenv("EMBEDDING_BUCKET", "embeddings")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None


class DatabaseUtils:
    """Utility class for database operations related to audio processing."""
    
    def __init__(self):
        """Initialize DatabaseUtils with encoder and directory setup."""
        self.encoder = VoiceEncoder()
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories if they don't exist."""
        directories = ['temp_audio', 'embeddings', 'sample', 'sample_embedding']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info("Directory structure initialized")
    
    def download_audio_from_supabase(
        self, 
        remote_path: str, 
        local_path: str
    ) -> bool:
        """
        Download audio file from Supabase storage to local storage.
        
        Args:
            remote_path: Path in Supabase storage
            local_path: Local path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not supabase:
                logger.error("Supabase client not initialized")
                return False
            
            # Download file from storage
            response = supabase.storage.from_(AUDIO_BUCKET).download(remote_path)
            
            # Write to local file
            with open(local_path, 'wb') as f:
                f.write(response)
            
            logger.info(f"Downloaded: {remote_path} -> {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return False
    
    def upload_embedding_to_supabase(
        self, 
        embedding: np.ndarray, 
        remote_path: str
    ) -> bool:
        """
        Upload vector embedding to Supabase storage.
        
        Args:
            embedding: Numpy array containing the embedding
            remote_path: Path in Supabase storage
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not supabase:
                logger.error("Supabase client not initialized")
                return False
            
            # Save embedding temporarily
            temp_file = 'temp_embedding.npy'
            np.save(temp_file, embedding)
            
            # Upload to Supabase
            with open(temp_file, 'rb') as f:
                supabase.storage.from_(EMBEDDING_BUCKET).upload(
                    remote_path, 
                    f, 
                    file_options={"content-type": "application/octet-stream"}
                )
            
            # Clean up temp file
            os.remove(temp_file)
            
            logger.info(f"Uploaded embedding: {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading embedding: {e}")
            if os.path.exists('temp_embedding.npy'):
                os.remove('temp_embedding.npy')
            return False
    
    def delete_local_audio(self, local_path: str) -> bool:
        """
        Delete audio file from local storage.
        
        Args:
            local_path: Path to the local file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                logger.info(f"Deleted local file: {local_path}")
                return True
            else:
                logger.warning(f"File not found: {local_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def download_all_embeddings(self, local_dir: str = 'embeddings') -> List[str]:
        """
        Download all embedding files from Supabase storage.
        
        Args:
            local_dir: Directory to save embeddings
            
        Returns:
            List of local file paths
        """
        downloaded_files = []
        
        try:
            if not supabase:
                logger.error("Supabase client not initialized")
                return downloaded_files
            
            # List all files in embedding bucket
            files = supabase.storage.from_(EMBEDDING_BUCKET).list()
            
            for file_info in files:
                remote_path = file_info['name']
                local_path = os.path.join(local_dir, remote_path)
                
                # Download embedding
                response = supabase.storage.from_(EMBEDDING_BUCKET).download(remote_path)
                
                # Save locally
                with open(local_path, 'wb') as f:
                    f.write(response)
                
                downloaded_files.append(local_path)
                logger.info(f"Downloaded embedding: {remote_path}")
            
            logger.info(f"Downloaded {len(downloaded_files)} embeddings")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Error downloading embeddings: {e}")
            return downloaded_files
    
    def convert_to_wav(self, input_path: str, output_path: str) -> bool:
        """
        Convert audio file to WAV format.
        
        Args:
            input_path: Path to input audio file
            output_path: Path to output WAV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(1)  # Mono
            audio = audio.set_frame_rate(16000)  # 16kHz sample rate
            audio.export(output_path, format='wav')
            logger.info(f"Converted to WAV: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error converting to WAV: {e}")
            return False
    
    def process_single_audio(
        self, 
        audio_filename: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Process a single audio file: download, convert, embed, upload.
        
        Args:
            audio_filename: Name of the audio file in Supabase
            
        Returns:
            Tuple of (success: bool, embedding_path: str or None)
        """
        local_audio_path = None
        wav_path = None
        embedding_path = None
        
        try:
            # Step 1: Download audio
            local_audio_path = os.path.join('temp_audio', audio_filename)
            if not self.download_audio_from_supabase(audio_filename, local_audio_path):
                return False, None
            
            # Step 2: Convert to WAV
            base_name = os.path.splitext(audio_filename)[0]
            wav_path = os.path.join('temp_audio', f"{base_name}.wav")
            if not self.convert_to_wav(local_audio_path, wav_path):
                return False, None
            
            # Step 3: Generate embedding
            wav = preprocess_wav(wav_path)
            embedding = self.encoder.embed_utterance(wav)
            
            # Step 4: Upload embedding to Supabase
            embedding_filename = f"{base_name}_embedding.npy"
            if not self.upload_embedding_to_supabase(embedding, embedding_filename):
                return False, None
            
            # Step 5: Save embedding locally
            embedding_path = os.path.join('embeddings', embedding_filename)
            np.save(embedding_path, embedding)
            
            logger.info(f"Successfully processed: {audio_filename}")
            return True, embedding_path
            
        except Exception as e:
            logger.error(f"Error processing audio {audio_filename}: {e}")
            return False, None
            
        finally:
            # Clean up temporary files
            if local_audio_path and os.path.exists(local_audio_path):
                self.delete_local_audio(local_audio_path)
            if wav_path and os.path.exists(wav_path):
                self.delete_local_audio(wav_path)
    
    def process_all_database_audios(self) -> int:
        """
        Process all audio files in the database.
        Downloads, converts, embeds, and re-uploads all audio files.
        
        Returns:
            int: Number of successfully processed files
        """
        processed_count = 0
        
        try:
            if not supabase:
                logger.error("Supabase client not initialized")
                return 0
            
            # List all files in audio bucket
            files = supabase.storage.from_(AUDIO_BUCKET).list()
            logger.info(f"Found {len(files)} audio files to process")
            
            for file_info in files:
                filename = file_info['name']
                success, _ = self.process_single_audio(filename)
                if success:
                    processed_count += 1
            
            logger.info(f"Processed {processed_count}/{len(files)} audio files")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error processing database audios: {e}")
            return processed_count
    
    def initialize_embeddings(self) -> bool:
        """
        Initialize the system by processing all database audios
        and downloading embeddings locally.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("Starting embedding initialization...")
            
            # Process all audios
            processed = self.process_all_database_audios()
            if processed == 0:
                logger.warning("No audio files processed")
                return False
            
            # Download all embeddings
            downloaded = self.download_all_embeddings()
            logger.info(f"Initialization complete: {processed} processed, {len(downloaded)} downloaded")
            
            return processed > 0
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False


# Convenience functions for direct usage
def download_audio(remote_path: str, local_path: str) -> bool:
    """Download audio from Supabase."""
    db_utils = DatabaseUtils()
    return db_utils.download_audio_from_supabase(remote_path, local_path)


def upload_embedding(embedding: np.ndarray, remote_path: str) -> bool:
    """Upload embedding to Supabase."""
    db_utils = DatabaseUtils()
    return db_utils.upload_embedding_to_supabase(embedding, remote_path)


def initialize_system() -> bool:
    """Initialize the entire system."""
    db_utils = DatabaseUtils()
    return db_utils.initialize_embeddings()


if __name__ == "__main__":
    # Run initialization when executed directly
    logger.info("Starting database initialization...")
    db_utils = DatabaseUtils()
    success = db_utils.initialize_embeddings()
    
    if success:
        logger.info("✓ Database initialization completed successfully")
    else:
        logger.error("✗ Database initialization failed")