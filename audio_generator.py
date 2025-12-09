#!/usr/bin/env python3
"""
Audio Generator for Meshtastic Voice Broadcasting
Creates simple WAV files for testing voice transmission
"""

import wave
import struct
import math
import numpy as np
from gtts import gTTS
import os

class AudioGenerator:
    """Generate audio files for Meshtastic broadcasting"""
    
    @staticmethod
    def generate_tone(filename='test_tone.wav', frequency=440, duration=2, 
                     sample_rate=8000, amplitude=0.5):
        """
        Generate a simple sine wave tone
        Low sample rate for bandwidth efficiency
        """
        print(f"Generating tone: {frequency}Hz, {duration}s...")
        
        n_samples = int(sample_rate * duration)
        
        # Generate sine wave
        samples = []
        for i in range(n_samples):
            value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            # Convert to 16-bit integer
            sample = int(value * 32767)
            samples.append(sample)
        
        # Write WAV file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            # Pack samples
            for sample in samples:
                wav_file.writeframes(struct.pack('<h', sample))
        
        file_size = os.path.getsize(filename)
        print(f"✓ Generated {filename} ({file_size} bytes)")
        return filename
    
    @staticmethod
    def text_to_speech(text, filename='voice_message.wav', 
                       language='en', slow=False):
        """
        Convert text to speech using Google TTS
        Then downsample for efficient transmission
        """
        print(f"Generating speech from text...")
        print(f"Text: {text}")
        
        try:
            # Generate speech with gTTS
            temp_file = 'temp_speech.mp3'
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(temp_file)
            
            # Convert MP3 to WAV with low sample rate using ffmpeg
            import subprocess
            
            # Convert to low sample rate WAV (8kHz, mono, 16-bit)
            cmd = [
                'ffmpeg', '-i', temp_file,
                '-ar', '8000',  # 8kHz sample rate
                '-ac', '1',     # Mono
                '-sample_fmt', 's16',  # 16-bit
                '-y',           # Overwrite
                filename
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Clean up temp file
            os.remove(temp_file)
            
            file_size = os.path.getsize(filename)
            print(f"✓ Generated {filename} ({file_size} bytes)")
            
            return filename
            
        except ImportError:
            print("✗ gtts not installed. Install with: pip install gtts")
            return None
        except FileNotFoundError:
            print("✗ ffmpeg not found. Install ffmpeg to convert audio.")
            return None
        except Exception as e:
            print(f"✗ Speech generation failed: {e}")
            return None
    
    @staticmethod
    def create_message_package(text_message, voice_message=None,
                              output_prefix='mesh_broadcast'):
        """
        Create a complete message package with text and optional voice
        """
        print("\n" + "="*60)
        print("CREATING MESSAGE PACKAGE")
        print("="*60)
        
        package = {
            'text': text_message,
            'text_file': f'{output_prefix}_text.txt',
            'voice_file': None
        }
        
        # Save text message
        with open(package['text_file'], 'w') as f:
            f.write(text_message)
        print(f"✓ Text saved to {package['text_file']}")
        
        # Generate voice if text provided
        if voice_message:
            voice_file = f'{output_prefix}_voice.wav'
            result = AudioGenerator.text_to_speech(voice_message, voice_file)
            if result:
                package['voice_file'] = voice_file
        
        return package
    
    @staticmethod
    def analyze_audio_file(filename):
        """Analyze WAV file for transmission planning"""
        try:
            with wave.open(filename, 'rb') as wav_file:
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                duration = n_frames / framerate
                
                audio_data = wav_file.readframes(n_frames)
                size_bytes = len(audio_data)
                
                # Estimate transmission time (200 bytes per chunk, 2 seconds per chunk)
                import base64
                encoded_size = len(base64.b64encode(audio_data))
                chunks = math.ceil(encoded_size / 200)
                estimated_time = chunks * 2  # seconds
                
                print("\n" + "="*60)
                print(f"AUDIO FILE ANALYSIS: {filename}")
                print("="*60)
                print(f"Format:")
                print(f"  Channels: {channels}")
                print(f"  Sample width: {sample_width} bytes")
                print(f"  Frame rate: {framerate} Hz")
                print(f"  Duration: {duration:.2f} seconds")
                print(f"\nSize:")
                print(f"  Raw audio: {size_bytes:,} bytes")
                print(f"  Base64 encoded: {encoded_size:,} bytes")
                print(f"\nTransmission estimate:")
                print(f"  Number of chunks: {chunks}")
                print(f"  Estimated time: {estimated_time:.0f} seconds (~{estimated_time/60:.1f} minutes)")
                print(f"  Bandwidth needed: {size_bytes/duration:.0f} bytes/second")
                
                if size_bytes > 1024 * 1024:  # 1 MB
                    print(f"\n⚠️  WARNING: File is large ({size_bytes/1024/1024:.2f} MB)")
                    print(f"   Consider reducing sample rate or duration")
                
                return {
                    'channels': channels,
                    'sample_width': sample_width,
                    'framerate': framerate,
                    'duration': duration,
                    'size_bytes': size_bytes,
                    'encoded_size': encoded_size,
                    'chunks': chunks,
                    'estimated_transmission_seconds': estimated_time
                }
                
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            return None


def main():
    """Main function with examples"""
    print("\n" + "="*60)
    print("MESHTASTIC AUDIO GENERATOR")
    print("="*60)
    
    # Example 1: Generate a simple test tone
    print("\n1. Generating test tone...")
    AudioGenerator.generate_tone(
        filename='test_tone.wav',
        frequency=440,  # A4 note
        duration=1,     # 1 second
        sample_rate=8000
    )
    
    # Example 2: Create text-to-speech message
    print("\n2. Generating voice message...")
    message_text = """
    Attention all mesh network nodes. 
    Discovery cascade complete. 
    All nodes are now catalogued and connected. 
    Thank you for participating in this network.
    """
    
    # Try to generate speech
    voice_file = AudioGenerator.text_to_speech(
        text=message_text.strip(),
        filename='discovery_complete.wav'
    )
    
    if voice_file:
        AudioGenerator.analyze_audio_file(voice_file)
    
    # Example 3: Create complete message package
    print("\n3. Creating message package...")
    package = AudioGenerator.create_message_package(
        text_message="🎯 Mesh Discovery Complete! All nodes found and catalogued.",
        voice_message="Discovery complete. All mesh nodes have been found and catalogued.",
        output_prefix='mesh_discovery'
    )
    
    print("\n" + "="*60)
    print("MESSAGE PACKAGE CREATED")
    print("="*60)
    print(f"Text file: {package['text_file']}")
    print(f"Voice file: {package['voice_file']}")
    
    print("\n💡 TIP: Use these files with the cascade discovery script:")
    print("   python meshtastic_cascade_discovery.py")


if __name__ == "__main__":
    main()
