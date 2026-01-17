import pytest
import sys

def test_imports():
    """Test that all modules can be imported."""
    try:
        sys.path.append(os.path.join(os.getcwd(), 'src'))
        from app import app
        from main import process_video
        from audio_analyzer import AudioAnalyzer
        from vision_engine import VisionEngine
    except ImportError as e:
        pytest.fail(f"Could not import modules: {e}")
