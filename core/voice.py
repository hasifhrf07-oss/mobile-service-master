"""
import threading
"""

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class Voice:
    def __init__(self, lang="bn", rate=160):
        self.lang = lang
        self.rate = rate
        self._lock = threading.Lock()

        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", rate)
                voices = self.engine.getProperty("voices")
                self.voice_id = None
                for v in voices:
                    if lang == "bn" and ("bengali" in v.name.lower() or
                                          "bangla" in v.name.lower()):
                        self.voice_id = v.id
                        break
                    if lang == "en" and "english" in v.name.lower():
                        self.voice_id = v.id
                        break
                if self.voice_id:
                    self.engine.setProperty("voice", self.voice_id)
            except Exception:
                self.engine = None
        else:
            self.engine = None

    def speak(self, text, async_mode=True):
        if not self.engine:
            print(f"🔈 [VOICE] {text}")
            return
        if async_mode:
            t = threading.Thread(target=self._speak_sync, args=(text,),
                                 daemon=True)
            t.start()
        else:
            self._speak_sync(text)

    def _speak_sync(self, text):
        with self._lock:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass

    def speak_device(self, info):
        parts = []
        if info.brand:
            parts.append(f"ব্র্যান্ড {info.brand}")
        if info.model:
            parts.append(f"মডেল {info.model}")
        if info.chipset:
            parts.append(f"চিপসেট {info.chipset}")
        if info.is_clone:
            parts.append("সতর্কতা — এটি ক্লোন ফোন")
        elif info.clone_reasons:
            parts.append("সন্দেহজনক ডিভাইস")
        if parts:
            self.speak(", ".join(parts))

    def stop(self):
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass 