import wave
import struct

# Create a simple WAV file
with wave.open('test_audio.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 2 bytes per sample
    wav_file.setframerate(16000)  # 16kHz sample rate
    
    # Generate 1 second of silence
    frames = b''.join([struct.pack('<h', 0) for _ in range(16000)])
    wav_file.writeframes(frames)

print('Created test_audio.wav')