VoiceSegmentation: 使用ASR进行语音分割，将长音频文件切分成短音频文件。

./results: 存放分割后的音频文件。带有resampled后缀的文件是重采样后的文件。

config.py: 配置文件，包含了所有的配置参数。

seg.py: 语音分割的主程序。

segmentation.py: 语音分割的主程序（不含api_key）。

wav_info.py: 读取wav文件的信息。

wav_resample.py: 重采样wav文件。
