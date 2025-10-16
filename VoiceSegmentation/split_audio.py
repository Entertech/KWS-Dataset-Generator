import os
import librosa
import soundfile as sf
import numpy as np

# --- 配置参数 ---
# 要处理的文件夹路径
INPUT_DIR = "C:/Users/Win11/Downloads/CHiME6/S13" 
# 拆分后片段保存的文件夹路径
OUTPUT_DIR = "F:/1.6s_voice/CHiME6/S13"
# 每个片段的时长（秒）
CLIP_DURATION_SEC = 1.60

def split_and_save_audio(input_file, output_folder, duration_sec):
    """
    加载一个WAV文件，将其拆分成指定时长的片段，并保存到新的文件夹。
    """
    try:
        # 1. 加载音频文件
        # sr=None 保留原始采样率
        y, sr = librosa.load(input_file, sr=16000)
    except Exception as e:
        print(f"  [错误] 无法加载文件 {os.path.basename(input_file)}: {e}")
        return

    # 2. 计算每个片段的样本数
    samples_per_clip = int(sr * duration_sec)
    
    # 3. 计算可以拆分的片段总数
    num_clips = len(y) // samples_per_clip
    
    # 提取原始文件名 (不带扩展名)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    print(f"  -> 原始音频时长: {len(y)/sr:.2f}s, 拆分 {num_clips} 个片段...")

    # 4. 遍历并保存每个片段
    for i in range(num_clips):
        start_sample = i * samples_per_clip
        end_sample = start_sample + samples_per_clip
        
        # 截取音频片段
        clip = y[start_sample:end_sample]
        
        # 构造新的文件名：原始文件名_片段序号.wav
        output_filename = os.path.join(
            output_folder, 
            f"{base_name}_clip_{i+1:03d}.wav"
        )
        
        # 保存为 WAV 文件
        sf.write(output_filename, clip, sr)
    
    # 提示：如果文件末尾不足一个片段时长，该部分会被丢弃

# --- 主执行逻辑 ---
if __name__ == "__main__":
    print("--- WAV 音频文件拆分工具 ---")

    # 1. 创建输出文件夹（如果不存在）
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"创建输出文件夹: {OUTPUT_DIR}")
        
    # 2. 遍历输入文件夹
    processed_count = 0
    
    for root, _, files in os.walk(INPUT_DIR):
        # 计算当前子目录相对路径，并在输出根目录下镜像创建
        rel_path = os.path.relpath(root, INPUT_DIR)
        dest_dir = os.path.join(OUTPUT_DIR, rel_path)
        os.makedirs(dest_dir, exist_ok=True)

        for filename in files:
            if filename.lower().endswith(".wav"):
                input_filepath = os.path.join(root, filename)
                print(f"正在处理: {input_filepath}")
                split_and_save_audio(input_filepath, dest_dir, CLIP_DURATION_SEC)
                processed_count += 1

    print(f"\n--- 处理完成！共处理 {processed_count} 个音频文件。---")
