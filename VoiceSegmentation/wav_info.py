import os
import librosa
import numpy as np
import soundfile as sf
import pandas as pd


def analyze_wav_files(folder_path):
    """
    分析指定文件夹中的所有WAV文件

    参数:
    folder_path (str): WAV文件所在的文件夹路径

    返回:
    pandas.DataFrame: 包含所有WAV文件详细信息的数据框
    """
    # 存储音频文件信息的列表
    audio_info_list = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 确保是WAV文件
        if filename.lower().endswith('.wav'):
            file_path = os.path.join(folder_path, filename)

            try:
                # 使用librosa读取音频文件
                y, sr = librosa.load(file_path, sr=None)

                # 使用soundfile获取更多文件细节
                audio_info = sf.info(file_path)

                # 准备单个音频文件的信息字典
                file_details = {
                    '文件名': filename,
                    '文件路径': file_path,
                    '采样率 (Hz)': sr,
                    '总时长 (秒)': len(y) / sr,
                    '声道数': audio_info.channels,
                    '采样点数': len(y),
                    '数据类型': str(y.dtype),
                    '比特深度': audio_info.subtype_info[0],
                }

                audio_info_list.append(file_details)

            except Exception as e:
                print(f"处理文件 {filename} 时发生错误: {e}")

    # 将音频文件信息转换为DataFrame
    df = pd.DataFrame(audio_info_list)
    return df


def save_analysis_results(df, output_path=None):
    """
    保存分析结果

    参数:
    df (pandas.DataFrame): 音频文件分析结果
    output_path (str, 可选): 输出文件路径
    """
    # 如果未指定输出路径，默认保存为CSV
    if output_path is None:
        output_path = 'wav_files_analysis.csv'

    # 保存为CSV文件
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"分析结果已保存到 {output_path}")


# 使用示例
if __name__ == '__main__':
    # 指定包含WAV文件的文件夹路径
    wav_folder = 'D:/Project/LooktechVoice/Results/SPK001_resampled'

    # 分析文件夹中的WAV文件
    analysis_results = analyze_wav_files(wav_folder)

    # 打印分析结果
    print(analysis_results)

    # 可选：将结果保存到CSV
    save_analysis_results(analysis_results, wav_folder + '/wav_files_analysis.csv')
