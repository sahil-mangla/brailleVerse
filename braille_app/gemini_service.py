"""
Google Gemini AI Service Module for Braille Display Website

Uses the google-genai >= 1.0 SDK (new Client-based API).
"""

from django.conf import settings

# Try to import google-genai (1.x SDK)
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-genai not installed. Install with: pip install 'google-genai>=1.0.0'")


class GeminiService:
    """
    Service class for Google Gemini AI interactions.
    """

    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.api_available = (
            bool(self.api_key)
            and self.api_key not in ('YOUR_GEMINI_API_KEY_HERE', '')
            and GEMINI_AVAILABLE
        )

        if self.api_available:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("✓ Gemini AI client initialized (google-genai 1.x)")
            except Exception as e:
                print(f"✗ Gemini client init failed: {e}")
                self.api_available = False
        else:
            reasons = []
            if not GEMINI_AVAILABLE:
                reasons.append("google-genai not installed")
            if not self.api_key or self.api_key in ('YOUR_GEMINI_API_KEY_HERE', ''):
                reasons.append("GEMINI_API_KEY not set")
            print(f"✗ Gemini AI not available: {', '.join(reasons)}")

    def chat(self, message, conversation_history=None):
        """
        Send a message to Gemini and get a response.
        """
        if not self.api_available:
            return self._placeholder_response(message)

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=message,
            )
            return {
                'status': 'success',
                'response': response.text,
                'source': 'gemini',
            }
        except Exception as e:
            print(f"Gemini chat error: {e}")
            return {
                'status': 'error',
                'response': f"Sorry, I'm having trouble connecting to the AI right now. ({type(e).__name__}: {e})",
                'source': 'error',
            }

    def describe_image(self, image_path, prompt="Describe this image in detail for a visually impaired person."):
        """
        Generate a description of an image using Gemini Vision.
        """
        if not self.api_available:
            return {
                'status': 'success',
                'description': 'Placeholder: Gemini Vision API is not configured.',
                'source': 'placeholder',
            }

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Detect mime type from extension
            ext = image_path.rsplit('.', 1)[-1].lower()
            mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                        'gif': 'image/gif', 'webp': 'image/webp', 'bmp': 'image/bmp'}
            mime_type = mime_map.get(ext, 'image/jpeg')

            image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)

            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[image_part, prompt],
            )
            return {
                'status': 'success',
                'description': response.text,
                'source': 'gemini-vision',
            }
        except Exception as e:
            print(f"Gemini Vision error: {e}")
            return {
                'status': 'error',
                'description': f"Could not process image: {e}",
                'source': 'error',
            }

    def _placeholder_response(self, message):
        """Fallback responses when API is unavailable."""
        msg = message.lower()
        quick = {
            'hello': "Hello! How can I help you today?",
            'hi': "Hi there! What would you like to know?",
            'braille': "Braille is a tactile writing system used by visually impaired people, using raised dot patterns.",
            'help': "I'm an AI assistant. Ask me anything!",
        }
        for keyword, reply in quick.items():
            if keyword in msg:
                return {'status': 'success', 'response': reply, 'source': 'placeholder'}

        return {
            'status': 'success',
            'response': (
                f"You asked: '{message}'. "
                "The AI is currently unavailable — please ensure GEMINI_API_KEY is set "
                "in your Vercel environment variables."
            ),
            'source': 'placeholder',
        }


# Module-level singleton (recreated per serverless invocation — that's fine)
_gemini_service = None


def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
