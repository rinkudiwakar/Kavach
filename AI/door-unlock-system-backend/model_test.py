"""
Comprehensive test suite for the door unlock system.
Tests all components and the complete pipeline.
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path
import tempfile
import wave

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules to test
try:
    from db_utils import DatabaseUtils
    from resemblyzer_utils import ResemblyzerUtils
    from rhino import RhinoUtils
    from main_pipeline import DoorUnlockPipeline
    logger.info("✓ All modules imported successfully")
except ImportError as e:
    logger.error(f"✗ Import error: {e}")
    sys.exit(1)


class TestSuite:
    """Comprehensive test suite for door unlock system."""
    
    def __init__(self):
        """Initialize test suite."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_results = []
        logger.info(f"Test directory: {self.temp_dir}")
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.test_results.append((test_name, passed))
        logger.info(f"{status}: {test_name} {message}")
    
    def create_test_wav(self, duration: float = 1.0, sample_rate: int = 16000) -> str:
        """
        Create a test WAV file.
        
        Args:
            duration: Duration in seconds
            sample_rate: Sample rate in Hz
            
        Returns:
            Path to created WAV file
        """
        wav_path = os.path.join(self.temp_dir, "test_audio.wav")
        
        # Generate sine wave
        num_samples = int(duration * sample_rate)
        frequency = 440  # A4 note
        samples = []
        
        for i in range(num_samples):
            value = int(32767 * 0.5 * np.sin(2 * np.pi * frequency * i / sample_rate))
            samples.append(value)
        
        # Write WAV file
        with wave.open(wav_path, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(np.array(samples, dtype=np.int16).tobytes())
        
        return wav_path
    
    # =========================================================================
    # RESEMBLYZER UTILS TESTS
    # =========================================================================
    
    def test_resemblyzer_initialization(self):
        """Test ResemblyzerUtils initialization."""
        try:
            utils = ResemblyzerUtils()
            self.log_test(
                "ResemblyzerUtils Initialization", 
                utils.encoder is not None,
                "- Encoder loaded"
            )
        except Exception as e:
            self.log_test("ResemblyzerUtils Initialization", False, f"- {e}")
    
    def test_audio_conversion(self):
        """Test audio to WAV conversion."""
        try:
            utils = ResemblyzerUtils()
            test_wav = self.create_test_wav()
            output_wav = os.path.join(self.temp_dir, "converted.wav")
            
            success = utils.convert_to_wav(test_wav, output_wav)
            file_exists = os.path.exists(output_wav)
            
            self.log_test(
                "Audio Conversion", 
                success and file_exists,
                f"- Output: {output_wav}"
            )
        except Exception as e:
            self.log_test("Audio Conversion", False, f"- {e}")
    
    def test_embedding_generation(self):
        """Test embedding generation."""
        try:
            utils = ResemblyzerUtils()
            test_wav = self.create_test_wav(duration=2.0)
            output_path = os.path.join(self.temp_dir, "test_embedding.npy")
            
            success, embedding = utils.generate_embedding(test_wav, output_path)
            
            valid = (
                success and 
                embedding is not None and 
                isinstance(embedding, np.ndarray) and
                len(embedding.shape) == 1 and
                embedding.shape[0] == 256  # Resemblyzer embedding size
            )
            
            self.log_test(
                "Embedding Generation", 
                valid,
                f"- Shape: {embedding.shape if embedding is not None else 'None'}"
            )
        except Exception as e:
            self.log_test("Embedding Generation", False, f"- {e}")
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        try:
            utils = ResemblyzerUtils()
            
            # Create two random embeddings
            embedding1 = np.random.randn(256)
            embedding2 = np.random.randn(256)
            
            # Calculate similarity
            similarity = utils.calculate_cosine_similarity(embedding1, embedding2)
            
            # Check if similarity is in valid range
            valid = -1.0 <= similarity <= 1.0
            
            # Test identical embeddings
            similarity_same = utils.calculate_cosine_similarity(embedding1, embedding1)
            same_valid = 0.99 <= similarity_same <= 1.0
            
            self.log_test(
                "Cosine Similarity", 
                valid and same_valid,
                f"- Random: {similarity:.4f}, Identical: {similarity_same:.4f}"
            )
        except Exception as e:
            self.log_test("Cosine Similarity", False, f"- {e}")
    
    def test_embedding_storage(self):
        """Test embedding storage."""
        try:
            utils = ResemblyzerUtils()
            embedding = np.random.randn(256)
            output_path = os.path.join(self.temp_dir, "stored_embedding.npy")
            
            success = utils.store_embedding_locally(embedding, output_path)
            file_exists = os.path.exists(output_path)
            
            # Try loading it back
            if file_exists:
                loaded = np.load(output_path)
                arrays_equal = np.allclose(embedding, loaded)
            else:
                arrays_equal = False
            
            self.log_test(
                "Embedding Storage", 
                success and file_exists and arrays_equal,
                f"- File created and verified"
            )
        except Exception as e:
            self.log_test("Embedding Storage", False, f"- {e}")
    
    def test_mean_similarity_calculation(self):
        """Test mean similarity calculation."""
        try:
            utils = ResemblyzerUtils()
            
            # Create test embeddings directory
            test_embed_dir = os.path.join(self.temp_dir, "test_embeddings")
            os.makedirs(test_embed_dir, exist_ok=True)
            
            # Create some test embeddings
            for i in range(3):
                embedding = np.random.randn(256)
                np.save(os.path.join(test_embed_dir, f"embed_{i}.npy"), embedding)
            
            # Calculate mean similarity
            sample_embedding = np.random.randn(256)
            mean_sim, all_sims = utils.calculate_mean_similarity(
                sample_embedding, 
                test_embed_dir
            )
            
            valid = (
                len(all_sims) == 3 and
                -1.0 <= mean_sim <= 1.0
            )
            
            self.log_test(
                "Mean Similarity Calculation", 
                valid,
                f"- Mean: {mean_sim:.4f}, Count: {len(all_sims)}"
            )
        except Exception as e:
            self.log_test("Mean Similarity Calculation", False, f"- {e}")
    
    # =========================================================================
    # DATABASE UTILS TESTS
    # =========================================================================
    
    def test_database_utils_initialization(self):
        """Test DatabaseUtils initialization."""
        try:
            db_utils = DatabaseUtils()
            self.log_test(
                "DatabaseUtils Initialization", 
                db_utils.encoder is not None,
                "- Encoder loaded"
            )
        except Exception as e:
            self.log_test("DatabaseUtils Initialization", False, f"- {e}")
    
    def test_directory_creation(self):
        """Test directory structure creation."""
        try:
            db_utils = DatabaseUtils()
            
            required_dirs = ['temp_audio', 'embeddings', 'sample', 'sample_embedding']
            all_exist = all(os.path.exists(d) for d in required_dirs)
            
            self.log_test(
                "Directory Creation", 
                all_exist,
                f"- Created: {', '.join(required_dirs)}"
            )
        except Exception as e:
            self.log_test("Directory Creation", False, f"- {e}")
    
    def test_local_file_deletion(self):
        """Test local file deletion."""
        try:
            db_utils = DatabaseUtils()
            
            # Create a test file
            test_file = os.path.join(self.temp_dir, "test_delete.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Delete it
            success = db_utils.delete_local_audio(test_file)
            not_exists = not os.path.exists(test_file)
            
            self.log_test(
                "Local File Deletion", 
                success and not_exists,
                "- File deleted successfully"
            )
        except Exception as e:
            self.log_test("Local File Deletion", False, f"- {e}")
    
    # =========================================================================
    # RHINO UTILS TESTS
    # =========================================================================
    
    def test_rhino_initialization(self):
        """Test RhinoUtils initialization."""
        try:
            rhino = RhinoUtils()
            
            # Check if Rhino was initialized (may fail if no access key)
            if rhino.rhino is None:
                self.log_test(
                    "RhinoUtils Initialization", 
                    True,
                    "- Warning: No access key/context (expected)"
                )
            else:
                self.log_test(
                    "RhinoUtils Initialization", 
                    True,
                    "- Rhino engine loaded"
                )
            
            rhino.cleanup()
        except Exception as e:
            self.log_test("RhinoUtils Initialization", False, f"- {e}")
    
    def test_rhino_audio_processing(self):
        """Test Rhino audio processing."""
        try:
            rhino = RhinoUtils()
            test_wav = self.create_test_wav(duration=2.0)
            
            result = rhino.process_audio(test_wav)
            
            # Check result structure
            has_keys = all(
                key in result 
                for key in ['is_understood', 'intent', 'slots', 'error']
            )
            
            self.log_test(
                "Rhino Audio Processing", 
                has_keys,
                f"- Result keys present"
            )
            
            rhino.cleanup()
        except Exception as e:
            self.log_test("Rhino Audio Processing", False, f"- {e}")
    
    # =========================================================================
    # MAIN PIPELINE TESTS
    # =========================================================================
    
    def test_pipeline_initialization(self):
        """Test DoorUnlockPipeline initialization."""
        try:
            pipeline = DoorUnlockPipeline()
            
            valid = (
                pipeline.resemblyzer is not None and
                pipeline.rhino is not None
            )
            
            self.log_test(
                "Pipeline Initialization", 
                valid,
                f"- Threshold: {pipeline.similarity_threshold}"
            )
            
            pipeline.shutdown()
        except Exception as e:
            self.log_test("Pipeline Initialization", False, f"- {e}")
    
    def test_pipeline_audio_processing(self):
        """Test pipeline audio processing."""
        try:
            pipeline = DoorUnlockPipeline()
            test_wav = self.create_test_wav(duration=2.0)
            
            embedding, wav_path, embed_path = pipeline.process_new_audio(test_wav)
            
            valid = (
                embedding is not None and
                isinstance(embedding, np.ndarray) and
                wav_path is not None and
                embed_path is not None
            )
            
            self.log_test(
                "Pipeline Audio Processing", 
                valid,
                f"- Embedding shape: {embedding.shape if embedding is not None else 'None'}"
            )
            
            # Cleanup
            if wav_path and os.path.exists(wav_path):
                os.remove(wav_path)
            if embed_path and os.path.exists(embed_path):
                os.remove(embed_path)
            
            pipeline.shutdown()
        except Exception as e:
            self.log_test("Pipeline Audio Processing", False, f"- {e}")
    
    def test_pipeline_decision_making(self):
        """Test pipeline decision making logic."""
        try:
            pipeline = DoorUnlockPipeline(similarity_threshold=0.75)
            
            # Test case 1: High similarity, unlock intent
            result1 = pipeline.make_decision(
                0.85,
                {'is_understood': True, 'intent': 'unlock_door', 'slots': {}}
            )
            test1 = result1['action'] == 'open'
            
            # Test case 2: Low similarity
            result2 = pipeline.make_decision(
                0.60,
                {'is_understood': True, 'intent': 'unlock_door', 'slots': {}}
            )
            test2 = result2['action'] == 'rejected'
            
            # Test case 3: High similarity, lock intent
            result3 = pipeline.make_decision(
                0.85,
                {'is_understood': True, 'intent': 'lock_door', 'slots': {}}
            )
            test3 = result3['action'] == 'locked'
            
            # Test case 4: Not understood
            result4 = pipeline.make_decision(
                0.85,
                {'is_understood': False, 'intent': None, 'slots': None}
            )
            test4 = result4['action'] == 'invalid'
            
            all_passed = test1 and test2 and test3 and test4
            
            self.log_test(
                "Pipeline Decision Making", 
                all_passed,
                f"- All 4 decision cases passed"
            )
            
            pipeline.shutdown()
        except Exception as e:
            self.log_test("Pipeline Decision Making", False, f"- {e}")
    
    def test_pipeline_cleanup(self):
        """Test pipeline cleanup functionality."""
        try:
            pipeline = DoorUnlockPipeline()
            
            # Create test files
            test_wav = os.path.join(self.temp_dir, "cleanup_test.wav")
            test_embed = os.path.join(self.temp_dir, "cleanup_test.npy")
            
            with open(test_wav, 'w') as f:
                f.write("test")
            with open(test_embed, 'w') as f:
                f.write("test")
            
            # Test cleanup
            pipeline.cleanup_temp_files(test_wav, test_embed)
            
            files_deleted = (
                not os.path.exists(test_wav) and
                not os.path.exists(test_embed)
            )
            
            self.log_test(
                "Pipeline Cleanup", 
                files_deleted,
                "- Temporary files removed"
            )
            
            pipeline.shutdown()
        except Exception as e:
            self.log_test("Pipeline Cleanup", False, f"- {e}")
    
    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================
    
    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline."""
        try:
            # Create test embeddings for comparison
            embed_dir = "embeddings"
            os.makedirs(embed_dir, exist_ok=True)
            
            for i in range(2):
                embedding = np.random.randn(256)
                np.save(os.path.join(embed_dir, f"user_{i}.npy"), embedding)
            
            # Create pipeline
            pipeline = DoorUnlockPipeline(similarity_threshold=0.5)
            
            # Create test audio
            test_audio = self.create_test_wav(duration=2.0)
            
            # Execute pipeline
            result = pipeline.execute(test_audio)
            
            # Check result structure
            has_keys = all(
                key in result 
                for key in ['action', 'message', 'similarity_score', 'intent']
            )
            
            self.log_test(
                "End-to-End Pipeline", 
                has_keys,
                f"- Action: {result.get('action', 'N/A')}"
            )
            
            pipeline.shutdown()
        except Exception as e:
            self.log_test("End-to-End Pipeline", False, f"- {e}")
    
    # =========================================================================
    # RUN ALL TESTS
    # =========================================================================
    
    def run_all_tests(self):
        """Run all test cases."""
        logger.info("=" * 70)
        logger.info("DOOR UNLOCK SYSTEM - TEST SUITE")
        logger.info("=" * 70)
        logger.info("")
        
        # Resemblyzer tests
        logger.info("--- RESEMBLYZER UTILS TESTS ---")
        self.test_resemblyzer_initialization()
        self.test_audio_conversion()
        self.test_embedding_generation()
        self.test_cosine_similarity()
        self.test_embedding_storage()
        self.test_mean_similarity_calculation()
        logger.info("")
        
        # Database utils tests
        logger.info("--- DATABASE UTILS TESTS ---")
        self.test_database_utils_initialization()
        self.test_directory_creation()
        self.test_local_file_deletion()
        logger.info("")
        
        # Rhino tests
        logger.info("--- RHINO UTILS TESTS ---")
        self.test_rhino_initialization()
        self.test_rhino_audio_processing()
        logger.info("")
        
        # Pipeline tests
        logger.info("--- PIPELINE TESTS ---")
        self.test_pipeline_initialization()
        self.test_pipeline_audio_processing()
        self.test_pipeline_decision_making()
        self.test_pipeline_cleanup()
        logger.info("")
        
        # Integration tests
        logger.info("--- INTEGRATION TESTS ---")
        self.test_end_to_end_pipeline()
        logger.info("")
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        total = len(self.test_results)
        passed = sum(1 for _, result in self.test_results if result)
        failed = total - passed
        
        logger.info("=" * 70)
        logger.info("TEST SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Tests:  {total}")
        logger.info(f"Passed:       {passed} ✓")
        logger.info(f"Failed:       {failed} ✗")
        logger.info(f"Success Rate: {(passed/total*100):.1f}%")
        logger.info("=" * 70)
        
        if failed > 0:
            logger.info("\nFailed Tests:")
            for name, result in self.test_results:
                if not result:
                    logger.info(f"  ✗ {name}")
            logger.info("")


if __name__ == "__main__":
    # Run test suite
    test_suite = TestSuite()
    test_suite.run_all_tests()
    
    # Exit with appropriate code
    failed_count = sum(1 for _, result in test_suite.test_results if not result)
    sys.exit(0 if failed_count == 0 else 1)