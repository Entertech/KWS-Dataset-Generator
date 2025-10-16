import os
import logging
import random
import numpy as np
import soundfile as sf
import librosa
import glob
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

class VoiceprintAugmenter:
    """声纹数据增强类，提供音频拼接和噪声增强方法"""
    
    def __init__(self, config=None):
        """初始化声纹增强器
        
        Args:
            config: 增强配置参数，如果为None则使用默认配置
        """
        self.config = config if config else self._get_default_config()
        self._validate_config()
        
    def _validate_config(self):
        """验证配置参数的有效性"""
        # 检查必要的配置项是否存在
        required_keys = ['aug_count', 'snrs', 'noise_dir', 'silence_padding', 'total_duration']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"配置中缺少必要的参数: {key}")
                
        # 验证参数类型和值范围
        if not isinstance(self.config['aug_count'], int) or self.config['aug_count'] < 0:
            raise ValueError("aug_count必须是非负整数")
            
        if not isinstance(self.config['snrs'], list) or len(self.config['snrs']) != 2:
            raise ValueError("snrs必须是包含两个元素的列表，表示最小和最大信噪比")
            
        if not isinstance(self.config['silence_padding'], list) or len(self.config['silence_padding']) != 2:
            raise ValueError("silence_padding必须是包含两个元素的列表，表示最小和最大静音长度")
            
        if not isinstance(self.config['total_duration'], (int, float)) or self.config['total_duration'] <= 0:
            raise ValueError("total_duration必须是正数，表示音频总长度（秒）")
    
    def _get_default_config(self):
        """获取默认的增强配置"""
        return {
            # 每个样本固定增强的数量，0表示不做增强
            'aug_count': 10,
            # 加噪信噪比范围（值越小噪声越大）
            'snrs': [-12, 18],
            # 噪声增强的噪声文件夹
            'noise_dir': 'F:/noise',
            # 拼接的空白音频长度（秒）
            'silence_padding': [0, 0],  # 前后各添加空白
            # 总音频长度（秒）
            'total_duration': 1.6,
        }

    
    def _add_noise(self, audio, sample_rate, snr=None, noise_file=None):
        """添加噪声增强
        
        Args:
            audio: 音频数据
            sample_rate: 采样率
            snr: 指定的信噪比，如果为None则使用随机值
            noise_file: 指定的噪声文件，如果为None则随机选择
            
        Returns:
            增强后的音频数据, 信噪比
        """
        # 获取噪声文件列表
        noise_dir = self.config['noise_dir']
        if not os.path.exists(noise_dir):
            logging.warning(f"噪声目录不存在: {noise_dir}，跳过噪声增强")
            return audio, None
            
        noise_files = glob.glob(os.path.join(noise_dir, "**/*.wav"), recursive=True)
        if not noise_files:
            logging.warning(f"噪声目录中没有WAV文件: {noise_dir}，跳过噪声增强")
            return audio, None
            
        # 随机选择一个噪声文件
        if noise_file is None:
            noise_file = random.choice(noise_files)
        
        try:
            # 加载噪声文件
            noise, noise_sr = sf.read(noise_file)
            
            # 如果噪声是立体声，转换为单声道
            if len(noise.shape) > 1:
                noise = np.mean(noise, axis=1)
                
            # 重采样噪声到与音频相同的采样率
            if noise_sr != sample_rate:
                noise = librosa.resample(noise, orig_sr=noise_sr, target_sr=sample_rate)
                
            # 如果噪声长度不够，循环填充
            while len(noise) < len(audio):
                noise = np.concatenate([noise, noise])
                
            # 截取与音频相同长度的噪声
            noise = noise[:len(audio)]
            
            # 计算音频能量和噪声能量
            audio_energy = np.sum(audio ** 2)
            noise_energy = np.sum(noise ** 2)
            
            # 设置信噪比
            if snr is None:
                snr = random.uniform(self.config['snrs'][0], self.config['snrs'][1])
            
            # 添加检查，防止除以零或负数开方
            if noise_energy <= 1e-20:  # 如果噪声能量接近于零
                logging.warning("噪声能量接近于零，跳过噪声增强")
                return audio, None
                
            noise_factor = np.sqrt(audio_energy / (noise_energy * 10 ** (snr / 10)))
            
            # 添加噪声
            noisy_audio = audio + noise * noise_factor
            
            # 归一化，避免爆音
            max_val = np.max(np.abs(noisy_audio))
            if max_val > 1.0:
                noisy_audio = noisy_audio / max_val
                
            return noisy_audio, snr
            
        except Exception as e:
            logging.error(f"添加噪声时出错: {e}，跳过噪声增强")
            return audio, None
    
    def _pad_and_concat_audio(self, audio, sample_rate):
        """在音频前后添加空白并调整总长度
        
        Args:
            audio: 音频数据
            sample_rate: 采样率
            
        Returns:
            处理后的音频数据
        """
        # 获取配置的空白长度范围和总长度
        silence_min, silence_max = self.config['silence_padding']
        total_duration = self.config['total_duration']
        
        # 随机生成前后空白的长度（秒）
        pre_silence_duration = 0.1  # random.uniform(silence_min, silence_max)
        post_silence_duration = random.uniform(silence_min, silence_max)
        
        # 计算空白的样本数
        pre_silence_samples = int(pre_silence_duration * sample_rate)
        post_silence_samples = int(post_silence_duration * sample_rate)
        
        # 创建空白音频（全零）
        pre_silence = np.zeros(pre_silence_samples)
        post_silence = np.zeros(post_silence_samples)
        
        # 拼接音频
        padded_audio = np.concatenate([pre_silence, audio, post_silence])
        
        # 计算总样本数
        total_samples = int(total_duration * sample_rate)
        
        # 如果拼接后的音频超过总长度，则截取中间部分
        if len(padded_audio) > total_samples:
            # 计算需要从每一侧截取的样本数
            excess_samples = len(padded_audio) - total_samples
            start_idx = excess_samples // 2
            padded_audio = padded_audio[start_idx:start_idx + total_samples]
        
        # 如果拼接后的音频不足总长度，则在末尾添加空白
        elif len(padded_audio) < total_samples:
            padding_needed = total_samples - len(padded_audio)
            padded_audio = np.concatenate([padded_audio, np.zeros(padding_needed)])
        
        return padded_audio
    
    def _augment_single_audio(self, audio_file, out_dir, sample_rate):
        """对单个音频文件进行增强
        
        Args:
            audio_file: 音频文件路径
            out_dir: 输出目录
            sample_rate: 目标采样率
            
        Returns:
            是否成功
        """
        try:
            # 加载音频文件
            audio, sr = sf.read(audio_file)
            
            # 如果音频是立体声，转换为单声道
            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)
                
            # 重采样到目标采样率
            if sr != sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=sample_rate)
            
            # 创建输出目录
            os.makedirs(out_dir, exist_ok=True)
            
            # 提取原始文件名的主体部分
            base_name = os.path.basename(audio_file)
            
            # 固定增强的数量
            aug_count = self.config['aug_count']
            if aug_count <= 0:
                return True  # 如果不需要增强，直接返回
            
            # 随机选择信噪比
            snr_min, snr_max = self.config['snrs']
            
            # 获取所有噪声文件
            noise_files = glob.glob(os.path.join(self.config['noise_dir'], "**/*.wav"), recursive=True)
            if not noise_files:
                logging.warning(f"噪声目录中没有WAV文件，跳过噪声增强")
                return True
            
            for i in range(aug_count):
                # 复制原始音频
                aug_audio = audio.copy()
                
                # 1. 先进行拼接和截取
                aug_audio = self._pad_and_concat_audio(aug_audio, sample_rate)
                
                # 2. 再添加噪声
                snr = random.uniform(snr_min, snr_max)  # 随机选择信噪比
                noise_file = random.choice(noise_files)  # 随机选择噪声文件
                aug_audio, actual_snr = self._add_noise(aug_audio, sample_rate, snr, noise_file)
                if actual_snr is None:  # 如果噪声增强失败，重试
                    i -= 1
                    continue
                
                # 构建参数字符串
                param_str = f"_padded_snr{int(actual_snr)}"
                
                # 保存增强后的音频
                ext = '.wav'  # 确保扩展名是.wav
                aug_file = os.path.join(out_dir, f"{base_name}{param_str}{ext}")
                sf.write(aug_file, aug_audio, sample_rate)
            
            return True
            
        except Exception as e:
            logging.error(f"处理文件 {audio_file} 时出错: {e}")
            return False
    
    def _process_audio_files(self, audio_files, out_dir, sample_rate, process_num):
        """并行处理多个音频文件
        
        Args:
            audio_files: 音频文件列表
            out_dir: 输出目录
            sample_rate: 采样率
            process_num: 处理线程数
        """
        total_files = len(audio_files)
        logging.info(f"开始处理 {total_files} 个音频文件，使用 {process_num} 个进程")
        
        with ProcessPoolExecutor(max_workers=process_num) as executor:
            futures = []
            for audio_file in audio_files:
                future = executor.submit(self._augment_single_audio, audio_file, out_dir, sample_rate)
                futures.append(future)
            
            # 显示进度
            completed = 0
            for future in futures:
                future.result()
                completed += 1
                if completed % 100 == 0 or completed == total_files:
                    logging.info(f"进度: {completed}/{total_files} ({completed/total_files*100:.2f}%)")
    
    def augment_data(self, data_dir, out_dir, sample_rate=16000, process_num=1):
        """对指定目录的音频数据进行增强
        
        Args:
            data_dir: 输入数据目录
            out_dir: 输出数据目录
            sample_rate: 采样率
            process_num: 处理线程数
        """
        os.makedirs(out_dir, exist_ok=True)
        
        # 获取所有WAV文件
        audio_files = glob.glob(os.path.join(data_dir, "**/*.wav"), recursive=True)
        
        if not audio_files:
            logging.warning(f"在目录 {data_dir} 中没有找到WAV文件")
            return
        
        # 处理音频文件
        self._process_audio_files(audio_files, out_dir, sample_rate, process_num)
        
        logging.info(f"数据增强完成，结果保存至: {out_dir}")

# 默认配置
train_aug_conf = VoiceprintAugmenter()._get_default_config()

if __name__ == '__main__':
    # 超参数设置
    process_num = min(20, multiprocessing.cpu_count())  # 启用多线程数，不超过CPU核心数
    sample_rate = 16000  # wav音频数据的采样率

    # 数据路径和增强配置参数设置
    data_dirs = [
        "F:/1.6svoice_HeyMemo"  # 使用Windows路径格式
    ]
    out_dir = "F:/1.6s_half_augment"

    # 设置日志级别、输出格式和输出内容等
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s %(filename)s:%(lineno)d %(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 创建增强器实例
    augmenter = VoiceprintAugmenter(train_aug_conf)
    
    # 处理每个数据目录
    for data_dir in data_dirs:
        augmenter.augment_data(
            data_dir=data_dir,
            out_dir=out_dir,
            sample_rate=sample_rate,
            process_num=process_num
        )
