VoiceSegmentation: 使用ASR进行语音分割，将长音频文件切分成短音频文件。

工作流程：
1. 读取长音频文件
2. 使用静音检测进行初步分割
3. 对分割后的片段进行进一步处理（如音量分析、语速分析）
4. 使用ASR识别语音内容
5. 保存处理后的短音频片段

segmentation.py: 语音分割的主程序。

wav_info.py: 用于读取和分析WAV文件的信息。

wav_resample.py: 用于重采样WAV文件。

output_audio: 文件夹，用于存放处理后的音频文件。
