import replicate
import os
import pandas as pd
import time
from tqdm import tqdm
import requests
import concurrent.futures
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建输出目录
output_dir = "orpheus_outputs"
os.makedirs(output_dir, exist_ok=True)

# Replicate API配置
os.environ["REPLICATE_API_TOKEN"] = "YOUR_REPLICATE_API_TOKEN"

# 预定义的文本列表
texts = [
    "Hey Memo. -- Take a picture. -- Stop recording.",
    "Hey Memo. -- Take a video. -- Stop recording.",
    "Hey Memo. -- Volume up. -- Volume down.",
    "Hey Memo. -- Volume down. -- Volume up.",
    "Hey Memo. -- Play. -- Pause. -- Next.",
    "Hey Memo. -- Next. -- Pause. -- Play.",
    "Hey Memo. -- Pause. -- Next. -- Play.",
    "Hey Memo. -- Next. -- Stop recording.",
    "Take a picture. -- Volume down. -- Play.",
    "Hey Memo. -- Take a video. -- Pause.",
    "Volume up. -- Stop recording. -- Next.",
    "Play. -- Hey Memo. -- Take a picture.",
    "Take a video. -- Pause. -- Volume down.",
    "Next. -- Hey Memo. -- Stop recording.",
    "Pause. -- Take a picture. -- Volume up.",
    "Stop recording. -- Play. -- Next."
]


def process_single_text(args):
    """
    处理单个文本生成任务

    参数:
    args: 包含任务参数的元组 (voice, voice_characteristics, text, text_idx, api_params)
    """
    voice, voice_characteristics, text, text_idx, api_params = args

    # 创建声音标识符的子目录
    voice_dir = os.path.join(output_dir, voice)
    os.makedirs(voice_dir, exist_ok=True)

    # 输出文件路径
    filename = os.path.join(voice_dir, f"text{text_idx + 1}.wav")

    try:
        logger.info(f"生成语音: 声音={voice}, 文本索引={text_idx + 1}")

        # 创建新的API客户端（避免并发问题）
        api = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

        # 设置API参数
        input_params = {
            "text": text,
            "voice": voice_characteristics,
            **api_params
        }

        # 调用API
        output = api.run(
            "lucataco/orpheus-3b-0.1-ft:79f2a473e6a9720716a473d9b2f2951437dbf91dc02ccb7079fb3d89b881207f",
            input=input_params
        )

        # 下载音频文件
        audio_url = output
        response = requests.get(audio_url)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            logger.info(f"已保存到 {filename}")

            return {
                "voice": voice,
                "text": text,
                "url": audio_url,
                "local_file": filename,
                "status": "success"
            }
        else:
            logger.error(f"下载失败: {response.status_code}")
            return {
                "voice": voice,
                "text": text,
                "status": "failed",
                "error": f"下载失败: {response.status_code}"
            }

    except Exception as e:
        logger.error(f"生成失败: {e}")
        return {
            "voice": voice,
            "text": text,
            "status": "failed",
            "error": str(e)
        }


def generate_speech_concurrent(prompt_csv_path, max_workers=5):
    """
    从CSV文件读取提示信息并并发生成语音

    参数:
    prompt_csv_path: 包含提示信息的CSV文件路径
    max_workers: 最大并发数
    """
    # 读取CSV文件
    try:
        prompts_df = pd.read_csv(prompt_csv_path)
        logger.info(f"成功读取{len(prompts_df)}条提示信息")
    except Exception as e:
        logger.error(f"读取CSV文件失败: {e}")
        return []

    # 检查CSV是否包含必要的列
    required_columns = ["identifier"]
    for col in required_columns:
        if col not in prompts_df.columns:
            logger.error(f"错误: CSV文件缺少必要的列 '{col}'")
            return []

    # 准备任务列表
    tasks = []

    # 对每个提示创建任务
    for index, row in prompts_df.iterrows():
        voice = row["identifier"]
        voice_characteristics = row["voice"]

        # 获取API参数
        api_params = {
            "top_p": row.get("top_p", 0.95),
            "temperature": row.get("temperature", 0.6),
            "max_new_tokens": 1000,
            "repetition_penalty": row.get("repetition_penalty", 1.1)
        }

        # 为每个文本创建任务
        for text_idx, text in enumerate(texts):
            tasks.append((voice, voice_characteristics, text, text_idx, api_params))

    # 使用线程池执行任务
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用tqdm显示进度
        futures = [executor.submit(process_single_text, task) for task in tasks]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="处理任务"):
            results.append(future.result())

    # 统计结果
    success_count = sum(1 for r in results if r.get("status") == "success")
    fail_count = sum(1 for r in results if r.get("status") == "failed")

    logger.info(f"\n生成完成: 成功={success_count}, 失败={fail_count}")

    return results


if __name__ == "__main__":
    csv_path = "sample_modified.csv"  # 修改为您的实际CSV路径

    # 并发生成语音
    results = generate_speech_concurrent(csv_path, max_workers=3)  # 根据API限制调整并发数
