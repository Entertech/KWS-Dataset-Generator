import os
import subprocess
import librosa
import soundfile as sf
import logging

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('audio_conversion')


def convert_audio_to_wav(file_path):
    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return None

    # 判断文件后缀
    if file_path.endswith('.wav.mp3'):
        return convert_mp3_to_wav(file_path)
    elif file_path.endswith('.wav.m4a'):
        return convert_m4a_to_wav(file_path)
    else:
        logger.error(f"不支持的文件格式: {file_path}, 必须以.wav.mp3或.wav.m4a结尾")
        return None


def convert_mp3_to_wav(file_path):
    # 提取基本文件名（去掉.wav.mp3）
    base_name = file_path[:-8]  # 移除'.wav.mp3'
    output_path = f"{base_name}.wav"

    logger.info(f"将MP3文件 {file_path} 转换为 {output_path}")

    try:
        # 方法2：使用ffmpeg（需要系统安装ffmpeg）
        command = ['ffmpeg', '-i', file_path, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', output_path]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"使用ffmpeg成功转换文件")
            return output_path
        else:
            logger.error(f"ffmpeg转换失败: {result.stderr}")
            return None

    except Exception as e:
        logger.error(f"转换过程中出错: {str(e)}")
        return None


def convert_m4a_to_wav(file_path):
    # 提取基本文件名（去掉.wav.m4a）
    base_name = file_path[:-8]  # 移除'.wav.m4a'
    output_path = f"{base_name}.wav"

    logger.info(f"将M4A文件 {file_path} 转换为 {output_path}")

    try:
        # 方法2：使用ffmpeg（需要系统安装ffmpeg）
        command = ['ffmpeg', '-i', file_path, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', output_path]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"使用ffmpeg成功转换文件")
            return output_path
        else:
            logger.error(f"ffmpeg转换失败: {result.stderr}")
            return None

    except Exception as e:
        logger.error(f"转换过程中出错: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    # 处理文件夹中的所有音频文件
    # input_folder = "E:/Download/SPK001"
    # converted_files = []
    # # 遍历文件夹
    # for filename in os.listdir(input_folder):
    #     file_path = os.path.join(input_folder, filename)
    #     # 只处理.wav.mp3和.wav.m4a文件
    #     if filename.endswith('.wav.mp3') or filename.endswith('.wav.m4a'):
    #         logger.info(f"发现需要转换的文件: {filename}")
    #         # 调用转换函数
    #         converted_file = convert_audio_to_wav(file_path)
    #         if converted_file:
    #             converted_files.append(converted_file)
    #             logger.info(f"成功转换: {filename}")
    #         else:
    #             logger.error(f"转换失败: {filename}")
    # 输出结果统计
    # print(
    #     f"总共转换: {len(converted_files)}/{len([f for f in os.listdir(input_folder) if f.endswith('.wav.mp3') or f.endswith('.wav.m4a')])} 个文件")

    specific_file = "E:/Download/SPK001/CAN_LONDON_MALE_29.wav.mp3"
    converted_file = convert_audio_to_wav(specific_file)

