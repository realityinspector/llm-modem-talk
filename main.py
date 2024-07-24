import os
import speech_recognition as sr
from pydub import AudioSegment
import wave
import numpy as np
import scipy.signal as signal
import io

def is_modem_sound(audio_data, sample_rate):
    # Check if the audio data contains modem-like frequencies
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    frequencies, _, _ = signal.spectrogram(audio_array, fs=sample_rate)
    modem_frequencies = [1200, 2400, 4800, 9600]  # Common modem frequencies
    return any(np.isin(modem_frequencies, frequencies))

def decode_modem_sound(audio_data, sample_rate):
    # Attempt to decode the modem sound using common encoding schemes
    # (This is a simplified example, you may need to implement actual modem decoding)
    encoding_schemes = ["ASCII", "UTF-8", "UTF-16"]
    for scheme in encoding_schemes:
        try:
            decoded_text = audio_data.decode(scheme)
            return decoded_text
        except UnicodeDecodeError:
            continue
    return None

def process_video(video_path):
    # Convert video to audio
    audio = AudioSegment.from_file(video_path, format="mp4")
    audio_path = "temp_audio.wav"
    audio.export(audio_path, format="wav")

    # Initialize speech recognizer
    recognizer = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    # Get the sample rate of the audio
    with wave.open(audio_path, "rb") as wav_file:
        sample_rate = wav_file.getframerate()

    # Convert audio data to bytes
    audio_bytes = io.BytesIO(audio_data.get_wav_data()).read()

    # Perform speech recognition and modem sound decoding
    transcription = []
    try:
        if is_modem_sound(audio_bytes, sample_rate):
            decoded_text = decode_modem_sound(audio_bytes, sample_rate)
            if decoded_text:
                transcription.append(("Modem Sound", decoded_text))
            else:
                transcription.append(("Modem Sound", "Unable to decode"))
        else:
            text = recognizer.recognize_sphinx(audio_data)
            transcription.append(("Human Speech", text))
    except sr.UnknownValueError:
        transcription.append(("Unknown", "Speech recognition could not understand the audio."))
    except sr.RequestError as e:
        transcription.append(("Error", f"Could not request results from the speech recognition service; {e}"))

    # Print the transcription with labels
    print("Transcription:")
    for label, text in transcription:
        print(f"{label}: {text}")

    # Clean up temporary files
    os.remove(audio_path)

# Main script
current_dir = os.path.dirname(__file__)
video_filename = "clip.mp4"  # Replace with your actual video file name
video_path = os.path.join(current_dir, video_filename)
process_video(video_path)