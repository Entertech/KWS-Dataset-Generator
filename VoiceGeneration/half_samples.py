import os
from pydub import AudioSegment
from pydub.utils import make_chunks
from pydub.silence import split_on_silence

def process_wav_files(source_dir, dest_dir):
    """
    Processes WAV files in the source directory to create half-word negative samples.

    For each WAV file, it detects the non-silent part, splits it in the middle, 
    prepends silence to each half to make the total duration 1.6s, and saves them 
    to the destination directory with a mirrored folder structure.

    Args:
        source_dir (str): The path to the source directory containing WAV files.
        dest_dir (str): The path to the destination directory to save processed files.
    """
    target_duration_ms = 1600
    target_samplerate_hz = 16000

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith(".wav"):
                source_file_path = os.path.join(root, file)
                
                relative_path = os.path.relpath(root, source_dir)
                dest_subdir = os.path.join(dest_dir, relative_path)
                if not os.path.exists(dest_subdir):
                    os.makedirs(dest_subdir)

                try:
                    audio = AudioSegment.from_wav(source_file_path)
                    
                    if audio.frame_rate != target_samplerate_hz:
                        audio = audio.set_frame_rate(target_samplerate_hz)

                    # --- 有声部分检测和分割 ---
                    # 使用 split_on_silence 来找到非静音部分
                    # min_silence_len: 最小静音长度（毫秒）
                    # silence_thresh: 静音阈值（低于此分贝数被认为是静音）
                    non_silent_parts = split_on_silence(
                        audio,
                        min_silence_len=100,  # 至少100ms的静音才算
                        silence_thresh=audio.dBFS - 16, # 比平均音量低16dBFS就算静音
                        keep_silence=100 # 保留100ms的静音作为缓冲
                    )

                    if not non_silent_parts:
                        print(f"Warning: No non-silent parts found in {file}. Skipping.")
                        continue

                    # 将所有非静音部分合并成一个
                    speech = sum(non_silent_parts, AudioSegment.silent(duration=0))

                    # 从语音部分的中间分割
                    midpoint = len(speech) // 2
                    half1 = speech[:midpoint]
                    half2 = speech[midpoint:]
                    # --- 结束 ---

                    for i, half in enumerate([half1, half2], 1):
                        silence_duration = target_duration_ms - len(half)
                        if silence_duration < 0:
                            print(f"Warning: Segment of {file} is longer than 1.6s. Truncating.")
                            half = half[:target_duration_ms]
                            silence_duration = 0
                        
                        silence = AudioSegment.silent(duration=silence_duration, frame_rate=target_samplerate_hz)
                        final_audio = silence + half
                        
                        new_filename = f"half{i}_{file}"
                        dest_file_path = os.path.join(dest_subdir, new_filename)
                        
                        final_audio.export(dest_file_path, format="wav")

                except Exception as e:
                    print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    # --- 配置 ---
    source_directories = [
        "../results_edgetts",
        "../results_orpheus",
        "../results_parlertts",
    ]
    parent_destination_directory = "F:/1.6s_half"
    # --- 配置结束 ---

    for source_dir in source_directories:
        if os.path.exists(source_dir):
            source_folder_name = os.path.basename(source_dir)
            destination_directory = os.path.join(parent_destination_directory, source_folder_name)
            
            print(f"Processing files from '{source_dir}' into '{destination_directory}'")
            process_wav_files(source_dir, destination_directory)
        else:
            print(f"Warning: Source directory '{source_dir}' not found. Skipping.")

    print("Processing complete.")