import os
import re
from pydub import AudioSegment


def extract_db_and_wps(file_path):
    """
    从音频文件中提取音量(dB)和语速(wps)值
    """
    try:
        # 加载音频文件
        audio = AudioSegment.from_file(file_path)

        # 计算音量(dB)
        volume_db = audio.dBFS

        # 计算语速(wps)（假设语速为音频时长的倒数，需根据实际需求调整）
        duration_sec = len(audio) / 1000  # 毫秒转秒
        word_count = len(audio.split_to_mono())  # 假设单声道片段数为单词数
        speech_rate = word_count / duration_sec if duration_sec > 0 else 0

        return round(volume_db, 1), round(speech_rate, 1)
    except Exception as e:
        print(f"提取音量和语速时出错: {e}")
        return None, None

def get_unique_file_path(file_path):
    """
    如果文件已存在，生成一个唯一的文件路径
    """
    base, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1
    return file_path

def rename_wav_files_with_audio_analysis(root_dir):
    """
    批量重命名wav文件，格式为：国家_城市_性别_年龄_LookAnd_xxdB_xxwps.wav
    从文件夹名中提取前4部分信息，从wav文件中提取dB和wps值
    """
    for folder_name in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder_name)

        # 确保是目录且格式正确
        if not os.path.isdir(folder_path) or len(folder_name.split('_')) < 4:
            continue

        # 提取文件夹名前4部分
        parts = folder_name.split('_')
        prefix = '_'.join(parts[:4])

        # 处理文件夹中的wav文件
        for filename in os.listdir(folder_path):
            if not filename.endswith('.wav'):
                continue

            file_path = os.path.join(folder_path, filename)

            # 提取音量(dB)和语速(wps)值
            volume_db, speech_rate = extract_db_and_wps(file_path)
            if volume_db is None or speech_rate is None:
                continue

            # 构建新文件名
            new_name = f"{prefix}_LookAnd_{volume_db:.1f}dB_{speech_rate:.1f}wps.wav"
            new_path = os.path.join(folder_path, new_name)
            # 确保新文件名唯一
            unique_path = get_unique_file_path(new_path)
            # 重命名文件
            os.rename(file_path, unique_path)
            print(f"重命名: {filename} -> {os.path.basename(unique_path)}")


if __name__ == "__main__":
    # 指定包含所有子文件夹的根目录
    root_directory = 'D:/LooktechVoice/VoiceGeneration/orpheus_outputs_new/'  # 替换为你的目录
    rename_wav_files_with_audio_analysis(root_directory)
    print("所有文件重命名完成！")
