class Config:
    """音频分割处理配置类"""
    
    # 微软ASR服务配置
    SPEECH_KEY = "你的Azure语音服务密钥"  # 请替换为你的密钥
    SPEECH_REGION = "eastus"  # 请替换为你的区域
    SPEECH_LANGUAGE = "en-US"
    
    # 文件路径配置
    INPUT_FOLDER = "input_audio"  # 输入音频文件夹
    OUTPUT_FOLDER = "output_audio"  # 输出音频文件夹
    TEST_FILE = "input_audio/AUS_Perth_Male_40.wav"  # 测试文件路径
    
    # 音频处理参数
    SAMPLE_RATE = 16000  # 采样率
    BIT_DEPTH = 16  # 位深度
    CHANNELS = 1  # 单声道
    BUFFER_MS = 200  # 切分音频时前后添加的缓冲区(毫秒)
    SILENCE_THRESHOLD = 0.01  # 静音判断阈值
    MAX_SILENCE_DURATION_MS = 500  # 最大允许静音时长(毫秒)
    MIN_AUDIO_DURATION_MS = 500  # 最小有效音频时长(毫秒)
    MAX_AUDIO_DURATION_MS = 3000  # 最大有效音频时长(毫秒) 
    MIN_VOLUME_DB = -30  # 最小音量阈值(dB)
    
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
    
    # 语速映射
    SPEED_MAPPING = {
        "fast": "Fast",
        "normal": "Normal",
        "slow": "Slow"
    }
