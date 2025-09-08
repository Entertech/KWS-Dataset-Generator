# KWS-Dataset-Generator
## 项目介绍
该项目是一个唤醒词语音数据集生成工具，主要包含两个核心模块：语音分割（VoiceSegmentation）和语音生成（VoiceGeneration）。该项目的目标是快速生成用于唤醒词语音数据集的音频文件。

## 功能模块
### 1. 语音分割 (VoiceSegmentation)
该模块使用ASR（自动语音识别）技术将长音频文件切分成短音频文件。
工作流程：
1. 读取长音频文件
2. 使用静音检测进行初步分割
3. 对分割后的片段进行进一步处理（如音量分析、语速分析）
4. 使用ASR识别语音内容
5. 保存处理后的短音频片段
### 2. 语音生成 (VoiceGeneration)
该模块提供多种语音合成方案，支持不同的TTS（文本到语音）引擎和声音特性定制。
 主要功能：
- 多种TTS引擎支持（Edge TTS、Orpheus、CosyVoice等）
- 多样化的声音特性（不同口音、语速、音量等）
- 批量生成语音文件
- 对话场景语音生成

## 项目结构
```
├── README.md                 # 项目主文档
├── requirements.txt          # 项目依赖
├── VoiceSegmentation/        # 语音分割模块
│   ├── README.md             # 语音分割模块文档
│   ├── config.py             # 配置文件
│   ├── segmentation.py       # 语音分割主程序
│   ├── wav_info.py           # WAV文件分析
│   ├── wav_resample.py       # WAV文件重采样
│   └── output_audio/         # 输出目录
├── VoiceGeneration/          # 语音生成模块
│   ├── cosyvoice.py          # CosyVoice引擎
│   ├── edgetts.py            # Edge TTS引擎
│   ├── orpheus.py            # Orpheus AI模型
│   ├── speaker_gen.py        # 说话人信息生成
└── └── dataset/              # 声音模型数据集
```

## 注意事项
- 使用语音分割功能需要配置Microsoft Azure语音服务的API密钥
- 部分语音生成引擎可能需要额外的API密钥或环境变量
- 处理大量音频文件时，请确保有足够的磁盘空间

## 项目特点
- 模块化设计，各功能相对独立
- 支持多种语音处理场景
- 可扩展性强，易于添加新的语音处理功能
- 详细的日志记录，便于调试和监控

