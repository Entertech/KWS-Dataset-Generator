class Config:
    """音频分割处理配置类"""

    # 微软ASR服务配置
    SPEECH_KEY = "ecc5c9b4f30b48adae8b2e5f3d519276"  # 请替换为你的密钥
    SPEECH_REGION = "westus2"  # 请替换为你的区域
    SPEECH_LANGUAGE = "en-US"

    # 文件路径配置
    INPUT_FOLDER = "E:/Download/Audio"  # 输入音频文件夹
    OUTPUT_FOLDER = "D:/LooktechVoice/results"  # 输出音频文件夹

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
        "Volume down",
        "Look and"
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
        "volume down": "VolumeDown",
        "look and": "LookAnd"
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
