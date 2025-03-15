from pydub import AudioSegment
from io import BytesIO
from google.oauth2 import service_account
from google.cloud import speech
import json
import os

# Load credentials from environment variable
def get_credentials():
    if 'GOOGLE_CREDENTIALS' in os.environ:
        # Parse credentials from environment variable
        credentials_dict = json.loads(os.environ['GOOGLE_CREDENTIALS'])
        return service_account.Credentials.from_service_account_info(credentials_dict)
    else:
        # Fall back to local file for development
        return service_account.Credentials.from_service_account_file("credentials/ai-tutors.json")

# Initialize credentials
credentials = get_credentials()

# Initialize the SpeechClient with the credentials
client = speech.SpeechClient(credentials=credentials)

def stt(audio_bytes) -> speech.RecognizeResponse:
    # Load the audio bytes into pydub and convert to 16-bit PCM WAV format
    audio_segment = AudioSegment.from_wav(BytesIO(audio_bytes)).set_sample_width(2)
    
    # Export the converted audio to a BytesIO object
    converted_audio_bytes = BytesIO()
    audio_segment.export(converted_audio_bytes, format="wav")
    converted_audio_bytes.seek(0)  # Reset the pointer to the beginning of the BytesIO object
    
    # Define the recognition configuration
    config = speech.RecognitionConfig(
        language_code="en", 
        profanity_filter=True, 
        enable_automatic_punctuation=True
    )
    
    # Use the pre-initialized client
    response = client.recognize(config=config, 
                                audio=speech.RecognitionAudio(content=converted_audio_bytes.read()))

    # Format the transcription into a single string
    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript + " "
    
    # Remove trailing space and return the transcription
    return transcription.strip()