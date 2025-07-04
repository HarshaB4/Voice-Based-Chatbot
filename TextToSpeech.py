import os
import time
import random
import logging
from pathlib import Path
from gtts import gTTS
from playsound import playsound  # Make sure this is installed: pip install playsound==1.2.2

class TextToSpeechAssistant:
    def __init__(self):
        self.audio_dir = Path("Data/Audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.current_file = None
        self.lock_file = self.audio_dir / "lockfile.tmp"
        self.max_attempts = 3

    def _cleanup_old_files(self):
        """Remove audio files older than 1 hour"""
        try:
            now = time.time()
            for file in self.audio_dir.glob("sound_*.mp3"):
                if (now - file.stat().st_mtime) > 3600:
                    try:
                        file.unlink()
                    except Exception as e:
                        self.logger.warning(f"Couldn't remove {file}: {e}")
        except Exception as e:
            self.logger.error(f"File cleanup error: {e}")

    def _wait_for_file_unlock(self):
        """Create a lock file to avoid simultaneous writes"""
        for _ in range(self.max_attempts):
            try:
                with open(self.lock_file, 'w') as f:
                    f.write(str(os.getpid()))
                return True
            except IOError:
                time.sleep(0.2)
        return False

    def generate_audio(self, text):
        """Generate audio file from text with retry logic"""
        if not text.strip():
            self.logger.warning("Empty text received for TTS.")
            return None

        self._cleanup_old_files()

        for attempt in range(self.max_attempts):
            try:
                timestamp = int(time.time())
                rand_suffix = random.randint(1000, 9999)
                audio_file = self.audio_dir / f"sound_{timestamp}_{rand_suffix}.mp3"

                if not self._wait_for_file_unlock():
                    raise IOError("Could not acquire file lock")

                tts = gTTS(text=text, lang='en')
                tts.save(audio_file)

                # Remove previous file
                if self.current_file and os.path.exists(self.current_file):
                    try:
                        os.remove(self.current_file)
                    except Exception as e:
                        self.logger.warning(f"Couldn't remove old file: {e}")

                self.current_file = str(audio_file)
                return self.current_file

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.max_attempts - 1:
                    return None
                time.sleep(0.5)

    def play_audio(self, audio_file):
        """Play audio file"""
        if not audio_file or not os.path.exists(audio_file):
            self.logger.error(f"Audio file not found: {audio_file}")
            return False

        try:
            for attempt in range(self.max_attempts):
                try:
                    playsound(audio_file, block=True)
                    time.sleep(0.1)
                    return True
                except Exception as e:
                    self.logger.warning(f"Playback attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_attempts - 1:
                        raise
                    time.sleep(0.3)
        except Exception as e:
            self.logger.error(f"Final playback failed: {e}")
            return False
        finally:
            try:
                if self.lock_file.exists():
                    os.remove(self.lock_file)
            except:
                pass

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.current_file and os.path.exists(self.current_file):
                os.remove(self.current_file)
            if self.lock_file.exists():
                os.remove(self.lock_file)
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
