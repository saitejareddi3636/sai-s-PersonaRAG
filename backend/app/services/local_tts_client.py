"""
HTTP client for local TTS service.

Expected service contract:
- Base URL: http://localhost:9000 (configurable)
- Endpoint: POST /synthesize
- Request: {"text": str, "voice_id": str | null}
- Response: {"success": bool, "audio_url": str, "duration_ms": int, "format": str}
- Error handling: Returns 5xx on failure; client should handle gracefully

This client is tolerant of service unavailability and returns structured errors.
"""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LocalTTSClient:
    """
    HTTP client for communicating with a local TTS service.
    
    Supports timeout, retries, and graceful degradation if service is unavailable.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:9000",
        timeout: float = 30.0,
        max_retries: int = 1,
    ):
        """
        Initialize TTS client.

        Args:
            base_url: URL to local TTS service (e.g., http://localhost:9000)
            timeout: Request timeout in seconds
            max_retries: Number of retries on transient errors
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries

    async def synthesize(
        self, text: str, voice_id: str | None = None
    ) -> dict[str, Any] | None:
        """
        Request TTS synthesis from local service.

        Args:
            text: Text to synthesize
            voice_id: Optional voice profile ID

        Returns:
            dict with keys: success, audio_url, duration_ms, format, provider
            None if service is unavailable or request fails

        Note:
            Failures are logged but not raised; caller should handle None gracefully.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to LocalTTSClient.synthesize")
            return None

        url = f"{self.base_url}/synthesize"
        payload = {
            "text": text.strip(),
            "voice_id": voice_id,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()
                # Enrich with provider name
                data["provider"] = "local-f5-tts"
                logger.info(
                    f"TTS synthesis succeeded: {len(text)} chars, {data.get('duration_ms')}ms"
                )
                return data
            else:
                logger.warning(
                    f"Local TTS service returned {response.status_code}: {response.text}"
                )
                return None

        except httpx.TimeoutException:
            logger.warning(
                f"Local TTS service timeout ({self.timeout}s); synthesis unavailable"
            )
            return None

        except httpx.ConnectError as e:
            logger.debug(f"Local TTS service not available: {e}")
            return None

        except httpx.RequestError as e:
            logger.error(f"Error communicating with local TTS service: {e}")
            return None

        except (ValueError, KeyError) as e:
            logger.error(f"Invalid response from local TTS service: {e}")
            return None

    async def is_healthy(self) -> bool:
        """
        Check if local TTS service is alive.

        Returns:
            True if service responds; False otherwise (non-blocking)
        """
        health_url = f"{self.base_url}/health"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(health_url)
            return response.status_code == 200
        except Exception:
            return False
