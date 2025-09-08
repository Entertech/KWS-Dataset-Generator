import asyncio
import os
import random
from edge_tts import Communicate, list_voices
from datetime import datetime

instructions = [
    "Hey Memo",
    "Next",
    "Pause",
    "Play",
    "Stop Recording",
    "Take A Picture",
    "Take A Video",
    "Volume Down",
    "Volume Up",
    "Look, And"
]

# VOICE_PROFILES 数组保持不变
VOICE_PROFILES = [
    {
        "voice": "en-AU-NatashaNeural",
        "country": "AUS",
        "city": "Sydney",
        "gender": "Female",
        "age": "25"
    },
    {
        "voice": "en-AU-WilliamNeural",
        "country": "AUS",
        "city": "Sydney",
        "gender": "Male",
        "age": "30"
    },
    {
        "voice": "en-CA-ClaraNeural",
        "country": "CAN",
        "city": "Montreal",
        "gender": "Female",
        "age": "30"
    },
    {
        "voice": "en-CA-LiamNeural",
        "country": "CAN",
        "city": "Montreal",
        "gender": "Male",
        "age": "20"
    },
    {
        "voice": "en-HK-YanNeural",
        "country": "UK",
        "city": "London",
        "gender": "Female",
        "age": "55"
    },
    {
        "voice": "en-HK-SamNeural",
        "country": "UK",
        "city": "London",
        "gender": "Male",
        "age": "55"
    },
    {
        "voice": "en-IN-NeerjaExpressiveNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Female",
        "age": "27"
    },
    {
        "voice": "en-IN-NeerjaNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Female",
        "age": "68"
    },
    {
        "voice": "en-IN-PrabhatNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Male",
        "age": "32"
    },
    {
        "voice": "en-IE-ConnorNeural",
        "country": "UK",
        "city": "London",
        "gender": "Male",
        "age": "50"
    },
    {
        "voice": "en-IE-EmilyNeural",
        "country": "UK",
        "city": "London",
        "gender": "Female",
        "age": "18"
    },
    {
        "voice": "en-KE-AsiliaNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Female",
        "age": "26"
    },
    {
        "voice": "en-KE-ChilembaNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Male",
        "age": "46"
    },
    {
        "voice": "en-NZ-MitchellNeural",
        "country": "AUS",
        "city": "Sydney",
        "gender": "Male",
        "age": "35"
    },
    {
        "voice": "en-NZ-MollyNeural",
        "country": "AUS",
        "city": "Sydney",
        "gender": "Female",
        "age": "50"
    },
    {
        "voice": "en-NG-AbeoNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Male",
        "age": "48"
    },
    {
        "voice": "en-NG-EzinneNeural",
        "country": "IND",
        "city": "Delhi",
        "gender": "Female",
        "age": "25"
    },
    {
        "voice": "en-PH-JamesNeural",
        "country": "USA",
        "city": "Miami",
        "gender": "Male",
        "age": "42"
    },
    {
        "voice": "en-PH-RosaNeural",
        "country": "USA",
        "city": "Miami",
        "gender": "Female",
        "age": "50"
    },
    {
        "voice": "en-US-AvaNeural",
        "country": "USA",
        "city": "Chicago",
        "gender": "Female",
        "age": "23"
    },
    {
        "voice": "en-US-AndrewNeural",
        "country": "USA",
        "city": "New York",
        "gender": "Male",
        "age": "33"
    },
    {
        "voice": "en-US-EmmaNeural",
        "country": "USA",
        "city": "Dallas",
        "gender": "Female",
        "age": "27"
    },
    {
        "voice": "en-US-BrianNeural",
        "country": "USA",
        "city": "Chicago",
        "gender": "Male",
        "age": "42"
    },
    {
        "voice": "en-SG-LunaNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Female",
        "age": "30"
    },
    {
        "voice": "en-SG-WayneNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Male",
        "age": "35"
    },
    {
        "voice": "en-ZA-LeahNeural",
        "country": "UK",
        "city": "London",
        "gender": "Female",
        "age": "26"
    },
    {
        "voice": "en-ZA-LukeNeural",
        "country": "UK",
        "city": "London",
        "gender": "Male",
        "age": "42"
    },
    {
        "voice": "en-TZ-ElimuNeural",
        "country": "USA",
        "city": "Dallas",
        "gender": "Male",
        "age": "30"
    },
    {
        "voice": "en-TZ-ImaniNeural",
        "country": "USA",
        "city": "Miami",
        "gender": "Female",
        "age": "28"
    },
    {
        "voice": "en-GB-LibbyNeural",
        "country": "UK",
        "city": "London",
        "gender": "Female",
        "age": "25"
    },
    {
        "voice": "en-GB-MaisieNeural",
        "country": "UK",
        "city": "London",
        "gender": "Female",
        "age": "22"
    },
    {
        "voice": "en-GB-RyanNeural",
        "country": "UK",
        "city": "London",
        "gender": "Male",
        "age": "35"
    },
    {
        "voice": "en-GB-SoniaNeural",
        "country": "UK",
        "city": "London",
        "gender": "Female",
        "age": "40"
    },
    {
        "voice": "en-GB-ThomasNeural",
        "country": "UK",
        "city": "London",
        "gender": "Male",
        "age": "75"
    },
    {
        "voice": "en-US-AnaNeural",
        "country": "USA",
        "city": "Miami",
        "gender": "Female",
        "age": "34"
    },
    {
        "voice": "en-US-AndrewMultilingualNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Male",
        "age": "26"
    },
    {
        "voice": "en-US-AriaNeural",
        "country": "USA",
        "city": "New York",
        "gender": "Female",
        "age": "48"
    },
    {
        "voice": "en-US-AvaMultilingualNeural",
        "country": "USA",
        "city": "New York",
        "gender": "Female",
        "age": "28"
    },
    {
        "voice": "en-US-BrianMultilingualNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Male",
        "age": "38"
    },
    {
        "voice": "en-US-ChristopherNeural",
        "country": "USA",
        "city": "Chicago",
        "gender": "Male",
        "age": "32"
    },
    {
        "voice": "en-US-EmmaMultilingualNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Female",
        "age": "26"
    },
    {
        "voice": "en-US-EricNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Male",
        "age": "29"
    },
    {
        "voice": "en-US-GuyNeural",
        "country": "USA",
        "city": "New York",
        "gender": "Male",
        "age": "35"
    },
    {
        "voice": "en-US-JennyNeural",
        "country": "USA",
        "city": "Dallas",
        "gender": "Female",
        "age": "28"
    },
    {
        "voice": "en-US-MichelleNeural",
        "country": "USA",
        "city": "Los Angeles",
        "gender": "Female",
        "age": "38"
    },
    {
        "voice": "en-US-RogerNeural",
        "country": "USA",
        "city": "New York",
        "gender": "Male",
        "age": "40"
    },
    {
        "voice": "en-US-SteffanNeural",
        "country": "USA",
        "city": "Dallas",
        "gender": "Male",
        "age": "31"
    }
]


async def generate_speech_with_variation(text, voice_profile, output_dir, variation_id,
                                         base_rate_type="Normal", base_volume="0"):
    """生成带变化的语音文件"""
    # 去除语句中的空格，用于文件名
    text_for_filename = text.replace(", ", "")

    # 对于每个变体，稍微调整语速和音量以创造差异
    # 使用variation_id作为基础，增加轻微随机变化
    random.seed(int(voice_profile['age']) + variation_id + len(text))

    # 根据基础速率类型设置实际速率值
    if base_rate_type == "Normal":
        rate_folder_name = "Normal"
        # Normal速率不传递速率参数
        rate_param = None
    elif base_rate_type == "Fast":
        rate_folder_name = "Fast"
        # 在8-12之间随机选择整数
        actual_rate = random.randint(5, 15)
        rate_param = f"+{actual_rate}%"
    elif base_rate_type == "Slow":
        rate_folder_name = "Slow"
        # 在8-12之间随机选择整数，但是负值
        actual_rate = random.randint(5, 15)
        rate_param = f"-{actual_rate}%"

    # 随机音量变化
    actual_volume = random.randint(0, 5)
    volume_param = f"+{actual_volume}%"

    # 构建文件夹名称
    folder_name = f"{voice_profile['country']}_{voice_profile['city']}_{voice_profile['gender']}_{voice_profile['age']}_{rate_folder_name}"
    folder_path = os.path.join(output_dir, folder_name)

    # 确保文件夹存在
    os.makedirs(folder_path, exist_ok=True)

    # 构建文件名，包含变体ID
    filename = f"{voice_profile['country']}_{voice_profile['city']}_{voice_profile['gender']}_{voice_profile['age']}_{text_for_filename}_var{variation_id}.wav"
    file_path = os.path.join(folder_path, filename)

    try:
        # 根据是否有速率参数创建communicate对象
        if rate_param is None:
            communicate = Communicate(
                text,
                voice_profile['voice'],
                volume=volume_param
            )
        else:
            communicate = Communicate(
                text,
                voice_profile['voice'],
                rate=rate_param,
                volume=volume_param
            )

        await communicate.save(file_path)
        return file_path
    except Exception as e:
        print(f"生成失败: {e}")
        # 添加延迟重试
        await asyncio.sleep(2)
        try:
            if rate_param is None:
                communicate = Communicate(
                    text,
                    voice_profile['voice'],
                    volume=volume_param
                )
            else:
                communicate = Communicate(
                    text,
                    voice_profile['voice'],
                    rate=rate_param,
                    volume=volume_param
                )
            await communicate.save(file_path)
            return file_path
        except Exception as e2:
            print(f"重试失败: {e2}")
            return None


async def batch_generate_with_variations(instructions, voice_profiles, output_dir="generated_speech",
                                         rate_types=["Normal", "Fast", "Slow"],
                                         variants_per_combo=30):
    """批量生成带变化的语音文件，为每个组合生成多个变体"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    # 存储生成的文件列表
    generated_files = []
    # 使用信号量控制并发数量，避免过多请求导致服务拒绝
    semaphore = asyncio.Semaphore(2)  # 同时最多2个请求

    async def limited_generate(text, profile, variation_id, rate_type):
        async with semaphore:
            return await generate_speech_with_variation(
                text, profile, output_dir, variation_id, rate_type
            )

    # 创建所有任务
    tasks = []
    for profile in voice_profiles:
        for rate_type in rate_types:
            for instruction in instructions:
                # 为每个组合生成多个变体
                for variant_id in range(1, variants_per_combo + 1):
                    tasks.append(limited_generate(
                        instruction, profile, variant_id, rate_type
                    ))

    # 执行所有任务，获取结果
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # 处理结果
    for result in results:
        if isinstance(result, Exception):
            print(f"错误: {result}")
        elif result:
            generated_files.append(result)
            print(f"已生成: {result}")

    return generated_files


async def main_async():
    """异步主函数"""
    # 定义变化参数
    rate_types = ["Normal", "Fast", "Slow"]  # 使用描述性标签而不是数值
    variants_per_combo = 30  # 每个组合生成30个变体

    # 运行批量生成
    await batch_generate_with_variations(
        instructions,
        VOICE_PROFILES,
        output_dir="edgetts_generated_new",
        rate_types=rate_types,
        variants_per_combo=variants_per_combo
    )


def main():
    """主函数"""
    try:
        # 设置全局随机种子，确保每次运行产生不同结果
        random.seed(datetime.now().timestamp())
        asyncio.run(main_async())
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()
