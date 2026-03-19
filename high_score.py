import base64
import binascii
import hashlib
import hmac
import json
from pathlib import Path


SAVE_FILE_NAME = ".fishfood_save.dat"
LEGACY_FILE_NAME = "high_score.txt"
SAVE_VERSION = 1
_SIGNING_KEY = b"FishFood::high-score::v1"


class HighScoreStore:
    def __init__(self, enabled=True, base_path=None):
        self.enabled = enabled
        self.base_path = Path(base_path) if base_path else Path(__file__).resolve().parent
        self.save_path = self.base_path / SAVE_FILE_NAME
        self.legacy_path = self.base_path / LEGACY_FILE_NAME

    def load(self):
        if not self.enabled:
            return 0

        score = self._load_signed_score()
        if score is not None:
            return score

        legacy_score = self._load_legacy_score()
        if legacy_score is not None:
            self.save(legacy_score)
            return legacy_score

        return 0

    def save(self, score):
        if not self.enabled:
            return 0

        safe_score = max(0, int(score))
        payload = {
            "score": safe_score,
            "version": SAVE_VERSION,
        }
        payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        signature = hmac.new(_SIGNING_KEY, payload_bytes, hashlib.sha256).hexdigest()
        encoded_payload = base64.urlsafe_b64encode(payload_bytes).decode("ascii")
        document = json.dumps(
            {"payload": encoded_payload, "signature": signature},
            separators=(",", ":"),
        )

        try:
            self.save_path.write_text(document, encoding="utf-8")
        except OSError:
            pass

        return safe_score

    def _load_signed_score(self):
        try:
            raw_document = self.save_path.read_text(encoding="utf-8")
            document = json.loads(raw_document)
            payload_text = document["payload"]
            signature = document["signature"]
            payload_bytes = base64.urlsafe_b64decode(payload_text.encode("ascii"))
            expected_signature = hmac.new(_SIGNING_KEY, payload_bytes, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return None

            payload = json.loads(payload_bytes.decode("utf-8"))
            if payload.get("version") != SAVE_VERSION:
                return None

            score = int(payload["score"])
            return max(0, score)
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
            binascii.Error,
        ):
            return None

    def _load_legacy_score(self):
        try:
            return max(0, int(self.legacy_path.read_text(encoding="utf-8").strip()))
        except (OSError, ValueError):
            return None
