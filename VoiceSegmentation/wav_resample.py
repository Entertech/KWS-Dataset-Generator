import os
import librosa
import soundfile as sf
import numpy as np


def resample_wav_file(input_path, output_path=None, target_sample_rate=16000):
    """
    重新采样WAV文件到指定的采样率

    参数:
    input_path (str): 输入WAV文件路径
    output_path (str, 可选): 输出WAV文件路径。如果为None，将在原文件名基础上添加采样率后缀
    target_sample_rate (int, 可选): 目标采样率，默认为16000 Hz

    返回:
    str: 输出文件的完整路径
    """
    try:
        # 读取原始音频文件
        # 使用sr=None保留原始采样率
        y, orig_sr = librosa.load(input_path, sr=None)

        # 重新采样
        y_resampled = librosa.resample(y, orig_sr=orig_sr, target_sr=target_sample_rate)

        # 确定输出路径
        if output_path is None:
            # 如果没有指定输出路径，在原文件名中添加采样率
            file_dir = os.path.dirname(input_path)
            file_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(file_dir, f"{file_name}_{target_sample_rate}Hz.wav")

        # 保存重采样后的音频文件
        sf.write(output_path, y_resampled, target_sample_rate)

        print(f"重采样完成：{input_path} -> {output_path}")
        print(f"原始采样率：{orig_sr} Hz, 目标采样率：{target_sample_rate} Hz")

        return output_path

    except Exception as e:
        print(f"重采样时发生错误: {e}")
        return None


def batch_resample_wav_files(input_folder, target_sample_rate=16000, output_folder=None):
    """
    批量重采样文件夹中的WAV文件

    参数:
    input_folder (str): 输入WAV文件所在文件夹
    target_sample_rate (int, 可选): 目标采样率，默认为16000 Hz
    output_folder (str, 可选): 输出文件夹。如果为None，将在原文件夹中创建

    返回:
    list: 重采样后的文件路径列表
    """
    # 如果未指定输出文件夹，在输入文件夹创建一个子文件夹
    if output_folder is None:
        output_folder = os.path.join(input_folder, f"resampled_{target_sample_rate}Hz")

    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 存储重采样后的文件路径
    resampled_files = []

    # 遍历输入文件夹中的文件
    for filename in os.listdir(input_folder):
        # 确保是WAV文件
        if filename.lower().endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # 重采样单个文件
            resampled_file = resample_wav_file(
                input_path,
                output_path=output_path,
                target_sample_rate=target_sample_rate
            )

            if resampled_file:
                resampled_files.append(resampled_file)

    return resampled_files


# 使用示例
if __name__ == '__main__':
    # 单文件重采样
    # input_file = '/path/to/input/audio.wav'
    # resample_wav_file(input_file, target_sample_rate=16000)
    # 单文件夹批量重采样
    # input_folder = 'D:/Project/LooktechVoice/results/SPK004'
    # output_folder = 'D:/Project/LooktechVoice/results/SPK004_resampled'
    # batch_resample_wav_files(input_folder, target_sample_rate=16000, output_folder=output_folder)

    # 多文件夹批量重采样
    for i in range(1, 154):
        file_number = str(i).zfill(3)
        input_folder = f'D:/Project/LooktechVoice/results/SPK{file_number}'
        output_folder = f'D:/Project/LooktechVoice/results/SPK{file_number}_resampled'
        batch_resample_wav_files(input_folder, target_sample_rate=16000, output_folder=output_folder)

