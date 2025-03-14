import os
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub import silence
import logging
from pathlib import Path
import time
import azure.cognitiveservices.speech as speechsdk
import re
import tempfile

# 设置日志格式
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('audio_processing')


class Config:
    """音频分割处理配置类"""

    # 微软ASR服务配置
    SPEECH_KEY = "YOUR_API_KEY"  # 请替换为你的密钥
    SPEECH_REGION = "westus2"  # 请替换为你的区域
    SPEECH_LANGUAGE = "en-US"

    # 文件路径配置
    INPUT_FOLDER = "E:/Download/Audio"  # 输入音频文件夹
    OUTPUT_FOLDER = "D:/project/LooktechVoice/results"  # 输出音频文件夹

    # 音频处理参数
    SAMPLE_RATE = 16000  # 采样率
    BIT_DEPTH = 16  # 位深度
    CHANNELS = 1  # 单声道

    # 分割参数
    MIN_SILENCE_LEN = 800  # 最小静音长度(毫秒)
    SILENCE_THRESH = -40  # 静音阈值(dB)
    KEEP_SILENCE = 300  # 保留静音部分(毫秒)
    MIN_SEGMENT_DURATION = 500  # 最小片段时长(毫秒)
    MAX_SEGMENT_DURATION = 2500  # 最大片段时长(毫秒)

    # 音量判断参数
    VOLUME_HIGH_THRESHOLD = -15  # 高音量阈值(dB)
    VOLUME_LOW_THRESHOLD = -25  # 低音量阈值(dB)

    # 语速判断参数
    FAST_THRESHOLD = 2.5  # 快速语速阈值（字/秒）
    SLOW_THRESHOLD = 1.5  # 缓慢语速阈值（字/秒）

    # 命令词列表
    KEYWORDS = [
        "Hey Memo",
        "Take a picture",
        "Take a video",
        "Stop recording",
        "Pause",
        "Next",
        "Play",
        "Volume up",
        "Volume down"
    ]

    # 命令词规范化映射
    KEYWORD_MAPPING = {
        "hey memo": "HeyMemo",
        "take a picture": "TakeAPicture",
        "take a video": "TakeAVideo",
        "stop recording": "StopRecording",
        "pause": "Pause",
        "next": "Next",
        "play": "Play",
        "volume up": "VolumeUp",
        "volume down": "VolumeDown"
    }

    # 音量映射
    VOLUME_MAPPING = {
        "high": "H",
        "normal": "N",
        "low": "L"
    }

    # 语速映射
    SPEED_MAPPING = {
        "fast": "F",
        "normal": "N",
        "slow": "S"
    }


class SpeechRecognizer:
    """语音识别类"""

    def __init__(self):
        """初始化语音识别器"""
        # 创建语音配置
        self.speech_config = speechsdk.SpeechConfig(
            subscription=Config.SPEECH_KEY,
            region=Config.SPEECH_REGION
        )
        # 设置识别语言
        self.speech_config.speech_recognition_language = Config.SPEECH_LANGUAGE

    def recognize_from_file(self, audio_file):
        """从文件识别语音"""
        # 创建音频配置
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file)

        # 创建语音识别器
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )

        logger.info(f"开始识别文件: {audio_file}")

        # 执行识别
        result = speech_recognizer.recognize_once_async().get()

        # 分析结果
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            recognized_text = result.text
            logger.info(f"识别结果: {recognized_text}")
            return recognized_text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logger.warning(f"无法识别语音: {result.no_match_details}")
            return ""
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            logger.error(f"识别取消: {cancellation.reason}")
            if cancellation.reason == speechsdk.CancellationReason.Error:
                logger.error(f"错误详情: {cancellation.error_details}")
            return ""

        return ""


class AudioAnalyzer:
    """音频分析类"""

    @staticmethod
    def analyze_volume(audio_file):
        """分析音频音量"""
        # 加载音频
        audio = AudioSegment.from_file(audio_file)

        # 计算RMS音量(dB)
        volume_db = audio.dBFS

        # 判断音量级别
        if volume_db >= Config.VOLUME_HIGH_THRESHOLD:
            volume_level = "high"
        elif volume_db <= Config.VOLUME_LOW_THRESHOLD:
            volume_level = "low"
        else:
            volume_level = "normal"

        logger.info(f"音频 {audio_file} 的音量为 {volume_db:.2f}dB, 级别: {volume_level}")
        return volume_level, volume_db

    @staticmethod
    def analyze_speech_rate(text, audio_duration_sec):
        """分析语速"""
        if not text or audio_duration_sec <= 0:
            return "normal", 0

        # 计算单词数（简单方法，按空格分割）
        words = text.strip().split()
        word_count = len(words)

        # 计算语速（单词/秒）
        speech_rate = word_count / audio_duration_sec

        # 判断语速级别
        if speech_rate >= Config.FAST_THRESHOLD:
            speed_level = "fast"
        elif speech_rate <= Config.SLOW_THRESHOLD:
            speed_level = "slow"
        else:
            speed_level = "normal"

        logger.info(f"语速: {speech_rate:.2f} 单词/秒, 级别: {speed_level}")
        return speed_level, speech_rate

    @staticmethod
    def match_keyword(text):
        """匹配关键词"""
        if not text:
            return None

        # 将文本转为小写并移除标点符号
        normalized_text = text.lower().strip()
        normalized_text = re.sub(r'[^\w\s]', '', normalized_text)

        # 尝试精确匹配
        for keyword in Config.KEYWORDS:
            keyword_lower = keyword.lower()
            if keyword_lower in normalized_text:
                mapped_keyword = Config.KEYWORD_MAPPING.get(keyword_lower, keyword)
                logger.info(f"匹配到关键词: {keyword} -> {mapped_keyword}")
                return mapped_keyword

        # 如果没有匹配，返回None
        logger.debug(f"未匹配到任何关键词, 原文: {text}")
        return None


class AudioSplitter:
    """音频分割类"""

    def __init__(self, input_folder=None, output_folder=None):
        """初始化音频分割器"""
        self.input_folder = input_folder or Config.INPUT_FOLDER
        self.output_folder = output_folder or Config.OUTPUT_FOLDER

        # 初始化语音识别器
        self.recognizer = SpeechRecognizer()

        # 确保输出文件夹存在
        os.makedirs(self.output_folder, exist_ok=True)

        # 临时文件列表，用于跟踪并在处理完成后删除
        self.temp_files = []

    def get_audio_files(self):
        """获取所有音频文件路径"""
        audio_files = []
        for root, _, files in os.walk(self.input_folder):
            for file in files:
                if file.endswith(('.wav', '.mp3', '.m4a', '.wav.mp3', '.wav.m4a')):
                    audio_files.append(os.path.join(root, file))
        return audio_files

    def extract_file_info(self, filename):
        """从文件名提取信息"""
        # 提取文件名（不包括扩展名）
        base_filename = os.path.basename(filename)
        name_without_ext = os.path.splitext(base_filename)[0]

        # 如果文件名是双扩展名如 xx.wav.mp3，需要额外处理
        if '.wav.' in base_filename:
            name_without_ext = base_filename.split('.wav.')[0]

        # 尝试拆分文件名部分
        parts = name_without_ext.split('_')

        if len(parts) >= 4:
            country = parts[0]
            city = parts[1]
            gender = parts[2]
            age = parts[3]

            return {
                "country": country,
                "city": city,
                "gender": gender,
                "age": age
            }
        else:
            logger.warning(f"文件名格式不正确: {filename}，使用默认值")
            return {
                "country": "UNK",
                "city": "UNK",
                "gender": "UNK",
                "age": "00"
            }

    def split_audio(self, audio_path):
        """根据静音分割音频"""
        logger.info(f"分割音频: {audio_path}")

        try:
            # 直接加载任何格式的音频
            if audio_path.endswith('.mp3'):
                audio = AudioSegment.from_mp3(audio_path)
            elif audio_path.endswith('.m4a'):
                audio = AudioSegment.from_file(audio_path, format="m4a")
            elif audio_path.endswith('.wav'):
                audio = AudioSegment.from_wav(audio_path)
            else:
                audio = AudioSegment.from_file(audio_path)

            # 根据静音分割
            chunks = silence.split_on_silence(
                audio,
                min_silence_len=Config.MIN_SILENCE_LEN,
                silence_thresh=Config.SILENCE_THRESH,
                keep_silence=Config.KEEP_SILENCE
            )

            logger.info(f"初步分割为 {len(chunks)} 个片段")

            # 处理分割结果
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                # 检查片段时长
                if len(chunk) < Config.MIN_SEGMENT_DURATION:
                    logger.debug(f"片段 {i + 1} 太短，跳过 ({len(chunk)}ms < {Config.MIN_SEGMENT_DURATION}ms)")
                    continue

                # 如果片段太长，进一步分割
                if len(chunk) > Config.MAX_SEGMENT_DURATION:
                    logger.debug(f"片段 {i + 1} 太长，进一步分割 ({len(chunk)}ms > {Config.MAX_SEGMENT_DURATION}ms)")
                    sub_chunks = self.split_long_chunk(chunk)
                    processed_chunks.extend(sub_chunks)
                else:
                    processed_chunks.append(chunk)

            logger.info(f"处理后得到 {len(processed_chunks)} 个有效片段")
            return processed_chunks

        except Exception as e:
            logger.error(f"分割音频失败: {str(e)}")
            return []

    def split_long_chunk(self, chunk):
        """将长音频片段进一步分割"""
        sub_chunks = []
        chunk_duration = len(chunk)

        # 计算需要分割成几个片段
        num_segments = (chunk_duration + Config.MAX_SEGMENT_DURATION - 1) // Config.MAX_SEGMENT_DURATION
        segment_duration = chunk_duration // num_segments

        # 分割
        for i in range(num_segments):
            start = i * segment_duration
            end = min((i + 1) * segment_duration, chunk_duration)
            sub_chunk = chunk[start:end]
            sub_chunks.append(sub_chunk)

        return sub_chunks

    def analyze_audio_segment(self, audio_chunk):
        """分析音频片段，识别关键词、音量和语速"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_path = temp_file.name
            self.temp_files.append(temp_path)

            # 保存音频片段到临时文件
            audio_chunk.export(temp_path, format="wav")

            # 分析音量
            volume_level, volume_db = AudioAnalyzer.analyze_volume(temp_path)

            # 语音识别
            recognized_text = self.recognizer.recognize_from_file(temp_path)

            # 分析语速
            duration_sec = len(audio_chunk) / 1000  # 毫秒转秒
            speed_level, speech_rate = AudioAnalyzer.analyze_speech_rate(recognized_text, duration_sec)

            # 匹配关键词
            matched_keyword = AudioAnalyzer.match_keyword(recognized_text)

            return {
                "text": recognized_text,
                "keyword": matched_keyword or "Unknown",
                "volume": {
                    "level": volume_level,
                    "db": volume_db,
                    "code": Config.VOLUME_MAPPING.get(volume_level, "N")
                },
                "speed": {
                    "level": speed_level,
                    "rate": speech_rate,
                    "code": Config.SPEED_MAPPING.get(speed_level, "N")
                }
            }

    def save_chunks(self, chunks, file_path, spk_id):
        """保存分割后的音频片段"""
        # 提取文件信息
        file_info = self.extract_file_info(file_path)

        # 创建保存目录
        folder_path = os.path.join(self.output_folder, f"SPK{spk_id:03d}")
        os.makedirs(folder_path, exist_ok=True)

        saved_files = []
        for i, chunk in enumerate(chunks):
            # 分析音频
            analysis = self.analyze_audio_segment(chunk)

            # 创建序号
            segment_num = f"{i + 1:03d}"

            # 创建文件名，格式：SPK001_CAN_LONDON_MALE_29_HeyMemo_-15.2dB_2.4wps.wav
            # 保留小数点后一位的音量(dB)和语速(单词/秒)
            volume_str = f"{analysis['volume']['db']:.1f}dB"
            speed_str = f"{analysis['speed']['rate']:.1f}wps"
            filename = f"SPK{spk_id:03d}_{file_info['country']}_{file_info['city']}_{file_info['gender']}_{file_info['age']}_{analysis['keyword']}_{volume_str}_{speed_str}.wav"
            output_path = os.path.join(folder_path, filename)

            # 保存音频
            chunk.export(output_path, format="wav")
            # 扩展保存的文件信息，添加更多详细数据
            saved_files.append({
                "path": output_path,
                "analysis": analysis,
                "volume_db": analysis['volume']['db'],
                "speech_rate": analysis['speed']['rate'],
                "filename": os.path.basename(output_path)
            })

            logger.info(f"已保存: {output_path}")

        return saved_files

    def process_file(self, file_path, spk_id):
        """处理单个文件"""
        logger.info(f"处理文件: {file_path}")

        # 分割音频
        chunks = self.split_audio(file_path)

        # 保存分割后的音频
        saved_files = self.save_chunks(chunks, file_path, spk_id)

        return {
            "input_file": file_path,
            "saved_files": saved_files
        }

    def process_batch(self, spk_id_start=1):
        """批量处理音频文件"""
        audio_files = self.get_audio_files()
        logger.info(f"发现 {len(audio_files)} 个音频文件")

        results = []
        for i, audio_path in enumerate(audio_files):
            spk_id = spk_id_start + i
            try:
                result = self.process_file(audio_path, spk_id)
                results.append(result)
            except Exception as e:
                logger.error(f"处理文件 {audio_path} 时出错: {str(e)}")

        # 删除所有临时文件
        self.cleanup_temp_files()

        return results

    def cleanup_temp_files(self):
        """清理所有临时文件"""
        logger.info(f"开始清理 {len(self.temp_files)} 个临时文件")

        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"已删除临时文件: {temp_file}")
            except Exception as e:
                logger.warning(f"删除临时文件失败: {temp_file}, 错误: {str(e)}")

        # 清空临时文件列表
        self.temp_files = []
        logger.info("临时文件清理完成")


# 执行批处理
def run_batch_processing(input_folder=None, output_folder=None, spk_id_start=1):
    """执行批处理"""
    logger.info("开始批量处理文件...")

    # 初始化分割器
    splitter = AudioSplitter(input_folder, output_folder)

    # 执行批处理
    results = splitter.process_batch(spk_id_start)

    # 汇总处理结果
    total_files = len(results)
    total_saved = sum(len(result['saved_files']) for result in results)

    # 统计关键词识别
    keyword_stats = {}
    volume_stats = {"high": 0, "normal": 0, "low": 0}
    speed_stats = {"fast": 0, "normal": 0, "slow": 0}

    # 检查是否有文件名冲突
    all_filenames = []
    duplicates = []

    for result in results:
        for file_info in result['saved_files']:
            # 关键词统计
            keyword = file_info['analysis']['keyword']
            if keyword in keyword_stats:
                keyword_stats[keyword] += 1
            else:
                keyword_stats[keyword] = 1

            # 音量和语速统计
            volume_stats[file_info['analysis']['volume']['level']] += 1
            speed_stats[file_info['analysis']['speed']['level']] += 1

            # 检查文件名冲突
            filename = os.path.basename(file_info['path'])
            if filename in all_filenames:
                duplicates.append(filename)
            else:
                all_filenames.append(filename)

    print("\n批处理结果汇总:")
    print(f"处理的文件总数: {total_files}")
    print(f"保存的文件总数: {total_saved}")
    print(f"平均每个文件的片段数: {total_saved / total_files if total_files > 0 else 0:.2f}")

    print("\n关键词识别统计:")
    for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"{keyword}: {count} 个片段")

    print("\n音量分布统计:")
    for level, count in volume_stats.items():
        print(f"{level.capitalize()}: {count} 个片段")

    print("\n语速分布统计:")
    for level, count in speed_stats.items():
        print(f"{level.capitalize()}: {count} 个片段")

    # 检查是否有文件名冲突
    if duplicates:
        print(f"\n警告: 发现 {len(duplicates)} 个重复文件名!")
        print("现在使用音量(dB)和语速(wps)的具体数值，应该不会再有冲突")

    return results


# 主程序入口
if __name__ == "__main__":
    print(f"使用配置参数:")
    print(f"输入文件夹: {Config.INPUT_FOLDER}")
    print(f"输出文件夹: {Config.OUTPUT_FOLDER}")
    print(f"语音识别服务: Azure ({Config.SPEECH_REGION})")

    # 执行批处理
    results = run_batch_processing()
