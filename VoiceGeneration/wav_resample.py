import os
import librosa
import soundfile as sf


def smart_resample(input_path, output_path=None, target_sample_rate=16000, preserve_structure=True):
    """
    智能重采样函数 - 自动检测输入类型并执行相应的重采样操作
    
    参数:
    input_path (str): 输入路径（可以是文件或文件夹）
    output_path (str, 可选): 输出路径。如果为None，将自动生成
    target_sample_rate (int): 目标采样率，默认16000 Hz
    preserve_structure (bool): 处理文件夹时是否保留目录结构，默认True
    
    返回:
    list: 重采样后的文件路径列表
    """
    resampled_files = []
    
    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        print(f"错误：路径 '{input_path}' 不存在")
        return resampled_files
    
    # 判断输入类型并执行相应操作
    if os.path.isfile(input_path):
        # 单文件处理
        if input_path.lower().endswith('.wav'):
            result = _resample_single_file(input_path, output_path, target_sample_rate)
            if result:
                resampled_files.append(result)
        else:
            print(f"警告：'{input_path}' 不是WAV文件")
    
    elif os.path.isdir(input_path):
        # 文件夹处理（自动递归）
        resampled_files = _resample_directory(input_path, output_path, target_sample_rate, preserve_structure)
    
    return resampled_files


def _resample_single_file(input_path, output_path=None, target_sample_rate=16000):
    """
    重采样单个WAV文件
    """
    try:
        # 读取音频文件
        y, orig_sr = librosa.load(input_path, sr=None)
        
        # 重新采样
        y_resampled = librosa.resample(y, orig_sr=orig_sr, target_sr=target_sample_rate)
        
        # 确定输出路径
        if output_path is None:
            file_dir = os.path.dirname(input_path)
            file_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(file_dir, f"{file_name}_{target_sample_rate}Hz.wav")
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存重采样后的音频文件
        sf.write(output_path, y_resampled, target_sample_rate)
        
        print(f"重采样完成：{os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        print(f"原始采样率：{orig_sr} Hz -> 目标采样率：{target_sample_rate} Hz")
        
        return output_path
    
    except Exception as e:
        print(f"重采样失败 {os.path.basename(input_path)}: {e}")
        return None


def _resample_directory(input_dir, output_dir=None, target_sample_rate=16000, preserve_structure=True):
    """
    递归重采样目录中的所有WAV文件
    """
    resampled_files = []
    
    # 确定输出目录
    if output_dir is None:
        parent_dir = os.path.dirname(input_dir)
        dir_name = os.path.basename(input_dir)
        output_dir = os.path.join(parent_dir, f"{dir_name}_resampled_{target_sample_rate}Hz")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"开始处理目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"目标采样率: {target_sample_rate} Hz")
    print(f"保留目录结构: {preserve_structure}")
    print("-" * 50)
    
    # 使用os.walk递归遍历所有文件
    for root, dirs, files in os.walk(input_dir):
        # 处理当前目录中的WAV文件
        wav_files = [f for f in files if f.lower().endswith('.wav')]
        
        if wav_files:
            # 确定当前文件的输出目录
            if preserve_structure:
                # 保留目录结构
                rel_path = os.path.relpath(root, input_dir)
                current_output_dir = os.path.join(output_dir, rel_path) if rel_path != '.' else output_dir
            else:
                # 所有文件放在同一个输出目录
                current_output_dir = output_dir
            
            # 创建输出目录
            os.makedirs(current_output_dir, exist_ok=True)
            
            # 处理每个WAV文件
            for wav_file in wav_files:
                input_file_path = os.path.join(root, wav_file)
                output_file_path = os.path.join(current_output_dir, wav_file)
                
                result = _resample_single_file(input_file_path, output_file_path, target_sample_rate)
                if result:
                    resampled_files.append(result)
    
    return resampled_files


def get_audio_info(file_path):
    """
    获取音频文件信息
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        duration = len(y) / sr
        return {
            'sample_rate': sr,
            'duration': duration,
            'samples': len(y)
        }
    except Exception as e:
        print(f"获取音频信息失败: {e}")
        return None


if __name__ == '__main__':
    # 使用示例
    # 方式1：处理单个文件
    # input_path = 'D:/LooktechVoice/test.wav'
    # smart_resample(input_path, target_sample_rate=16000)
    
    # 方式2：处理整个文件夹（递归，保留结构）
    input_path = 'D:/LooktechVoice/VoiceGeneration/edgetts_generated_new'
    output_path = 'D:/LooktechVoice/results_edgetts'
    
    resampled_files = smart_resample(
        input_path=input_path,
        output_path=output_path,
        target_sample_rate=16000,
        preserve_structure=True
    )
    
    print("-" * 50)
    print(f"重采样完成！共处理了 {len(resampled_files)} 个文件")
    if len(resampled_files) == 0:
        print("提示：没有找到需要重采样的WAV文件，请检查：")
        print("1. 输入路径是否正确")
        print("2. 目录中是否包含WAV文件")

