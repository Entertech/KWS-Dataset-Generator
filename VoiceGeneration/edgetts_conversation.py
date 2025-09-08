import asyncio
import os
import random
from edge_tts import Communicate, list_voices
from datetime import datetime
import wave
import subprocess

# Define two voices for the conversation
VOICE_PROFILES = [
    {
        "voice": "en-US-SteffanNeural",  # Male voice
        "country": "USA",
        "city": "Dallas",
        "gender": "Male",
        "age": "31"
    },
    {
        "voice": "en-US-JennyNeural",  # Female voice
        "country": "USA",
        "city": "Seattle",
        "gender": "Female",
        "age": "28"
    }
]

# Define the conversation script
# Format: List of tuples with (speaker_index, text)
# speaker_index: 0 for first voice, 1 for second voice
CONVERSATION = [
    (0, "Hey, have you seen that new documentary about space exploration?"),
    (1, "No, I haven't. What's it about?"),
    (0, "It covers everything from the early Apollo missions to the current plans for Mars colonization."),
    (1, "That sounds interesting! Are the visuals good?"),
    (0, "The visuals are absolutely stunning, especially the segments about the James Webb telescope."),
    (1,
     "I've been following some of the recent developments in astronomy. It's fascinating how much our understanding of the universe has changed."),
    (0, "Exactly! I'm thinking about joining an amateur astronomy club in our area."),
    (1, "Really? What do they do?"),
    (0,
     "They do monthly stargazing events at a spot about an hour outside the city where there's minimal light pollution."),
    (1, "That sounds amazing. Do they welcome beginners?"),
    (0,
     "Absolutely! They have several telescopes that members can use. Would you be interested in coming along sometime?"),
    (1, "I'd love to! Just let me know when the next event is.")
]


async def generate_speech(text, voice_profile, output_dir, filename, rate_param=None, volume_param="+0%"):
    """Generate a speech file with the given parameters"""
    folder_path = os.path.join(output_dir, "segments")
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, filename)

    try:
        # Create communicate object based on whether rate parameter is provided
        if rate_param is None:
            communicate = Communicate(
                text,
                voice_profile['voice'],
                volume=volume_param
            )
        else:
            communicate = Communicate(
                text,
                voice_profile['voice'],
                rate=rate_param,
                volume=volume_param
            )

        await communicate.save(file_path)
        return file_path
    except Exception as e:
        print(f"Generation failed: {e}")
        # Add delay and retry
        await asyncio.sleep(2)
        try:
            if rate_param is None:
                communicate = Communicate(
                    text,
                    voice_profile['voice'],
                    volume=volume_param
                )
            else:
                communicate = Communicate(
                    text,
                    voice_profile['voice'],
                    rate=rate_param,
                    volume=volume_param
                )
            await communicate.save(file_path)
            return file_path
        except Exception as e2:
            print(f"Retry failed: {e2}")
            return None


def generate_silence(duration_ms, output_path):
    """Generate a silent WAV file with specified duration in milliseconds"""
    # Parameters for the silent WAV
    channels = 1
    sample_width = 2  # 16-bit
    frame_rate = 24000  # 24 kHz (common for speech)

    # Calculate number of frames
    frames = int((duration_ms / 1000.0) * frame_rate)

    # Create silent frames (all zeros)
    silent_data = b'\x00' * (frames * channels * sample_width)

    # Write the WAV file
    with wave.open(output_path, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)
        wav_file.writeframes(silent_data)

    return output_path


async def generate_conversation(conversation, voice_profiles, output_dir="generated_conversation",
                                pause_duration=700, output_filename="conversation.wav"):
    """Generate a full conversation between two voices"""
    os.makedirs(output_dir, exist_ok=True)
    segments_dir = os.path.join(output_dir, "segments")
    os.makedirs(segments_dir, exist_ok=True)

    # First generate all speech segments
    segment_files = []
    tasks = []

    for i, (speaker_idx, text) in enumerate(conversation):
        # Get the voice profile for this speaker
        voice = voice_profiles[speaker_idx]

        # Add slight variations to each segment
        random.seed(i + int(voice['age']))
        volume_adjust = random.randint(0, 5)
        volume_param = f"+{volume_adjust}%"

        # Occasionally adjust rate for more natural speech
        rate_param = None
        if random.random() < 0.3:  # 30% chance to modify rate
            rate_adjust = random.randint(-5, 5)
            if rate_adjust != 0:
                rate_param = f"{'+' if rate_adjust > 0 else ''}{rate_adjust}%"

        # Create filename for this segment
        filename = f"segment_{i:02d}_{voice['gender']}.wav"

        # Add task to generate this segment
        tasks.append(generate_speech(
            text, voice, output_dir, filename, rate_param, volume_param
        ))

    # Run all generation tasks concurrently
    results = await asyncio.gather(*tasks)
    segment_files = [r for r in results if r is not None]

    if not segment_files:
        print("Failed to generate any segments")
        return None

    # Generate a silent pause file
    pause_file = os.path.join(segments_dir, "pause.wav")
    generate_silence(pause_duration, pause_file)

    # Create a file list for ffmpeg
    file_list_path = os.path.join(output_dir, "file_list.txt")
    with open(file_list_path, 'w') as f:
        for i, segment_file in enumerate(segment_files):
            f.write(f"file '{os.path.abspath(segment_file)}'\n")
            # Add pause after each segment except the last one
            if i < len(segment_files) - 1:
                f.write(f"file '{os.path.abspath(pause_file)}'\n")

    # Use ffmpeg to concatenate files
    output_path = os.path.join(output_dir, output_filename)
    cmd = [
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', file_list_path, '-c', 'copy', output_path
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Conversation saved to: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error concatenating audio files: {e}")
        print(f"FFmpeg stderr: {e.stderr.decode()}")
        return None


async def main_async():
    """Async main function"""
    # Run conversation generation
    await generate_conversation(
        CONVERSATION,
        VOICE_PROFILES,
        output_dir="generated_conversation",
        pause_duration=700,
        output_filename="two_voice_conversation.wav"
    )


def main():
    """Main function"""
    try:
        # Set global random seed for variety
        random.seed(datetime.now().timestamp())
        asyncio.run(main_async())
    except Exception as e:
        print(f"Program execution error: {e}")


if __name__ == "__main__":
    main()
