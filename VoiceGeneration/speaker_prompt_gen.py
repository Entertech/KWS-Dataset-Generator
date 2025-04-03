import pandas as pd
import numpy as np
import random

def generate_voice_characteristics(input_csv, output_csv, num_samples=None, seed=42):
    """
    从人口统计数据生成简化的语音特征描述
    
    参数:
    input_csv: 输入CSV文件路径，包含人口统计数据
    output_csv: 输出CSV文件路径，保存生成的语音特征
    num_samples: 要生成的样本数量，默认为None表示使用所有输入行
    seed: 随机种子
    
    返回:
    生成的语音特征DataFrame
    """
    np.random.seed(seed)
    random.seed(seed)
    
    # 读取人口统计数据
    df = pd.read_csv(input_csv)
    
    # 如果指定了数量，随机选择相应数量的行
    if num_samples is not None and num_samples < len(df):
        df = df.sample(num_samples)
    
    # 声音特征描述词汇库
    voice_qualities = {
        "tone": {
            "Male": ["deep", "resonant", "baritone", "tenor", "husky", "gravelly", "smooth", "rich", "warm", "strong"],
            "Female": ["melodic", "soprano", "alto", "bright", "warm", "clear", "soft", "rich", "smooth", "resonant"]
        },
        "emotion": ["neutral", "enthusiastic", "calm", "confident", "friendly", "professional", "thoughtful", "relaxed"],
        "pitch_variation": ["minimal pitch variation", "moderate pitch variation", "expressive pitch", "animated pitch", "monotone"],
        
        "age_descriptors": {
            (15, 24): ["youthful", "vibrant", "energetic", "fresh"],
            (25, 34): ["mature", "vibrant", "energetic", "confident"],
            (35, 44): ["mature", "well-developed", "confident", "established"],
            (45, 54): ["seasoned", "experienced", "mature", "self-assured"],
            (55, 64): ["refined", "mature", "seasoned", "experienced"],
            (65, 80): ["weathered", "mature", "dignified", "seasoned"]
        },
        
        # 口音特征描述
        "accent_traits": {
            "Westcoast US": {
                "description": "West Coast American accent",
                "traits": ["relaxed vowels", "California vowel shift", "minimal regional markers", "modern inflections"]
            },
            "Eastcoast US": {
                "description": "East Coast American accent",
                "traits": ["non-rhotic tendencies", "distinctive vowel sounds", "faster rhythm", "strong consonants"]
            },
            "Midwest US": {
                "description": "Midwestern American accent",
                "traits": ["nasal qualities", "flat 'a' sounds", "rounded 'o' vowels", "clear 'r' pronunciation"]
            },
            "South US": {
                "description": "Southern American accent",
                "traits": ["drawled vowels", "softened consonants", "melodic intonation", "distinctive rhythm"]
            },
            "Latin": {
                "description": "Latin American accent",
                "traits": ["Spanish-influenced rhythm", "rolled 'r' sounds", "distinctive vowel stress", "syllable-timed pattern"]
            },
            "French": {
                "description": "French accent",
                "traits": ["nasal vowels", "uvular 'r' sound", "even stress pattern", "distinct liaison"]
            },
            "England": {
                "description": "British English accent",
                "traits": ["non-rhotic pronunciation", "t-glottalization", "distinct vowel sounds", "crisp consonants"]
            },
            "India": {
                "description": "Indian accent",
                "traits": ["retroflex consonants", "syllable-timed rhythm", "distinctive stress patterns", "unique intonation"]
            },
            "Australia": {
                "description": "Australian accent",
                "traits": ["raised vowels", "non-rhotic pronunciation", "upward inflection", "distinctive diphthongs"]
            }
        },
        
        # 语速特征
        "rate_descriptors": {
            "Fast": ["rapid", "quick", "swift", "brisk", "accelerated"],
            "Normal": ["moderate", "measured", "standard", "conversational"],
            "Slow": ["unhurried", "deliberate", "measured", "leisurely"]
        }
    }
    
    # 生成语音特征
    voice_specs = []
    
    for _, row in df.iterrows():
        gender = row['gender']
        age = row['age']
        accent = row['accent']
        speech_rate = row['speech_rate']
        
        # 找到合适的年龄段描述词
        age_group = next((group for group in voice_qualities["age_descriptors"].keys() 
                          if group[0] <= age <= group[1]), (65, 80))
        
        # 随机选择特征描述词
        tone = random.choice(voice_qualities["tone"][gender])
        emotion = random.choice(voice_qualities["emotion"])
        pitch = random.choice(voice_qualities["pitch_variation"])
        age_desc = random.choice(voice_qualities["age_descriptors"][age_group])
        rate_desc = random.choice(voice_qualities["rate_descriptors"][speech_rate])
        
        # 提取口音特征
        accent_info = voice_qualities["accent_traits"][accent]
        accent_desc = accent_info["description"]
        accent_trait = random.choice(accent_info["traits"])
        
        # 构建简化的语音特征描述
        voice_char = (
            f"{age} year old {gender.lower()} with {tone}, {age_desc} voice. "
            f"{accent_desc} with {accent_trait}. "
            f"Clear, {emotion} speech at {rate_desc} speed with {pitch}."
        )
        
        # 创建结果记录
        spec = {
            "identifier": row['identifier'],
            "voice_characteristics": voice_char,
            "gender": gender,
            "age": age,
            "accent": accent,
            "speech_rate": speech_rate
        }
        
        voice_specs.append(spec)
    
    # 创建输出DataFrame
    result_df = pd.DataFrame(voice_specs)
    
    # 保存到CSV
    result_df.to_csv(output_csv, index=False, encoding='utf-8')
    
    return result_df


# 示例用法
if __name__ == "__main__":
    # 从sample.csv生成语音提示
    voice_specs = generate_voice_characteristics("sample.csv", "sample_prompt.csv")
    
    # 显示前5个语音特征
    # print("生成的简化语音特征示例:")
    # for i, (_, row) in enumerate(voice_specs.head(5).iterrows()):
    #     print(f"\n特征 #{i+1}:")
    #     print(f"标识符: {row['identifier']}")
    #     print(f"语音特征: {row['voice_characteristics']}")
