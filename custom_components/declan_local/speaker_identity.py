"""Authenticate speaker metadata bound to one transcript; never use for access control."""
import base64
import hashlib
import hmac
import json
import math
import re
import time


def unwrap(text, secret, profiles, seen, now=None):
    if not isinstance(text,str) or not text.startswith('JVS1.'):
        return text,None
    if not isinstance(secret,str) or not secret:
        return '',None
    match=re.fullmatch(r'JVS1\.([A-Za-z0-9_-]{1,8192})\.([a-f0-9]{64})',text)
    if not match:return '',None
    encoded,signature=match.groups()
    expected=hmac.new(secret.encode(),encoded.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature,expected):return '',None
    try:
        payload=json.loads(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4)))
        transcript=payload['text'];speaker=payload['speaker'];confidence=payload['confidence'];stamp=payload['time'];ident=payload['id']
        if not isinstance(transcript,str) or not isinstance(speaker,str) or not isinstance(ident,str) or not re.fullmatch(r'[0-9a-fA-F-]{36}',ident):return '',None
        if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not math.isfinite(confidence) or not 0<=confidence<=1:return '',None
        if isinstance(stamp,bool) or not isinstance(stamp,int):return '',None
        now=time.time() if now is None else now
        for key,expiry in list(seen.items()):
            if expiry<now:seen.pop(key,None)
        if abs(now-stamp)>30 or ident in seen:return '',None
        seen[ident]=now+60
        if len(seen)>512:seen.pop(next(iter(seen)))
        profile=profiles.get(speaker.casefold()) if isinstance(profiles,dict) else None
        if not isinstance(profile,dict):return transcript,None
        threshold=profile.get('min_confidence',0.75);name=profile.get('name')
        if isinstance(threshold,bool) or not isinstance(threshold,(int,float)) or not math.isfinite(threshold) or not 0<=threshold<=1:return transcript,None
        if confidence<threshold or not isinstance(name,str) or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ '-]{0,39}",name):return transcript,None
        return transcript,name
    except (ValueError,TypeError,KeyError,UnicodeDecodeError):return '',None


def bridge_profile(text, profiles):
    """Use bridge metadata only for optional response personalisation."""
    try:
        from .speaker_models import SpeakerTranscript
    except ImportError:
        return None
    if not isinstance(text, SpeakerTranscript):
        return None
    value = getattr(text, 'jarvis_speaker', None)
    if not isinstance(value, tuple) or len(value) != 3:
        return None
    _, speaker, confidence = value
    if not isinstance(speaker, str) or not isinstance(profiles, dict):
        return None
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        return None
    profile = profiles.get(speaker.casefold())
    if not isinstance(profile, dict):
        matches = [item for item in profiles.values() if isinstance(item, dict)
                   and isinstance(item.get('name'), str)
                   and item['name'].casefold() == speaker.casefold()]
        if len(matches) != 1:
            return None
        profile = matches[0]
    threshold = profile.get('min_confidence', 0.75)
    name = profile.get('name')
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0 <= threshold <= 1:
        return None
    if confidence < threshold or not isinstance(name, str) or not re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ '-]{0,39}", name):
        return None
    return name


class SatelliteSpeakerMemory:
    """Short-lived, per-satellite identity hints for conversation only.

    Never use the result to authorise actions or grant access. An explicit
    speaker disagreement invalidates the cached hint, even at low confidence.
    """

    def __init__(self, ttl=30, anchor_confidence=0.65):
        self.ttl = ttl
        self.anchor_confidence = anchor_confidence
        self._recent = {}

    def resolve(self, transcript, satellite_id, profiles, now=None, diagnostic=None):
        from .speaker_models import SpeakerTranscript

        def report(profile, source, confidence=None):
            if diagnostic is not None:
                diagnostic(profile, source, confidence)
            return profile

        now = time.monotonic() if now is None else now
        self._recent = {key: value for key, value in self._recent.items()
                        if now - value[1] < self.ttl}
        # A missing satellite must never share identity across devices.
        if not isinstance(satellite_id, str) or not satellite_id.strip():
            direct = bridge_profile(transcript, profiles)
            return report(direct, 'direct' if direct else 'unknown')

        direct = bridge_profile(transcript, profiles)
        metadata = getattr(transcript, 'jarvis_speaker', None) if isinstance(transcript, SpeakerTranscript) else None
        speaker = None
        confidence = None
        if isinstance(metadata, tuple) and len(metadata) == 3:
            _, raw_speaker, raw_confidence = metadata
            if isinstance(raw_speaker, str) and isinstance(raw_confidence, (int, float)) and not isinstance(raw_confidence, bool) and math.isfinite(raw_confidence) and 0 <= raw_confidence <= 1:
                speaker, confidence = raw_speaker.casefold(), raw_confidence

        previous = self._recent.get(satellite_id)
        if direct:
            if confidence is not None and confidence >= self.anchor_confidence:
                self._recent[satellite_id] = (speaker, now, direct)
            elif previous and speaker != previous[0]:
                self._recent.pop(satellite_id, None)
            return report(direct, 'direct', confidence)

        # A recogniser's explicit different identity is contradictory evidence.
        if speaker is not None and previous and speaker != previous[0]:
            self._recent.pop(satellite_id, None)
            return report(None, 'unknown', confidence)
        if not previous or not isinstance(transcript, SpeakerTranscript):
            return report(None, 'unknown', confidence)
        # Do not carry identity into long or unrelated requests.
        words = str(transcript).split()
        if not 1 <= len(words) <= 5:
            return report(None, 'unknown', confidence)
        # Missing metadata is permitted only for short, same-satellite follow-ups.
        return report(previous[2], 'memory', confidence)
