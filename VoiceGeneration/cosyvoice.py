import os
import time
import argparse
import base64
from typing import List, Dict
import dashscope
from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer


class BatchVoiceCloner:
    """批量语音克隆工具类"""

    def __init__(self, api_key: str = None, target_model: str = "cosyvoice-v1"):
        """
        初始化批量语音克隆工具

        Args:
            api_key: DashScope API密钥，若不提供则从环境变量获取
            target_model: 目标模型，默认为cosyvoice-v1
        """
        # 设置API密钥
        if api_key:
            dashscope.api_key = api_key
        else:
            dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
            if not dashscope.api_key:
                raise ValueError("API密钥未设置，请设置DASHSCOPE_API_KEY环境变量或直接提供api_key参数")

        print(f"API密钥已设置: {dashscope.api_key[:5]}...{dashscope.api_key[-5:] if dashscope.api_key else ''}")

        self.target_model = target_model
        self.service = VoiceEnrollmentService()

    def upload_local_file_to_data_uri(self, file_path: str) -> str:
        """
        将本地音频文件转换为data URI格式

        Args:
            file_path: 本地音频文件路径

        Returns:
            data URI格式的字符串
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')

        # 设置MIME类型
        mime_types = {
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'm4a': 'audio/mp4'
        }
        mime_type = mime_types.get(ext, 'audio/wav')

        # 读取文件并转换为Base64
        with open(file_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')

        # 构建data URI
        data_uri = f"data:{mime_type};base64,{encoded}"
        return data_uri

    def clone_voices(self, audio_files: Dict[str, str], prefix: str = "batch", use_local_files: bool = False) -> Dict[
        str, str]:
        """
        批量克隆多个声音

        Args:
            audio_files: 字典，键为音频标识名，值为音频URL或本地文件路径
            prefix: 音色自定义前缀，仅允许数字和小写字母，小于十个字符
            use_local_files: 是否使用本地文件

        Returns:
            字典，键为音频标识名，值为生成的voice_id
        """
        results = {}
        total = len(audio_files)

        print(f"开始批量克隆 {total} 个声音...")

        for i, (name, file_path) in enumerate(audio_files.items(), 1):
            try:
                print(f"[{i}/{total}] 正在克隆: {name}")
                # 创建自定义前缀，加入名称以便区分
                custom_prefix = f"{prefix}-{name}"[:10].lower()
                # 确保前缀只包含数字和小写字母
                custom_prefix = ''.join(c for c in custom_prefix if c.isdigit() or c.islower())

                # 处理本地文件
                if use_local_files:
                    if not os.path.exists(file_path):
                        print(f"  × 文件不存在: {file_path}")
                        continue

                    print(f"  正在处理本地文件: {file_path}")
                    url = self.upload_local_file_to_data_uri(file_path)
                    print(f"  文件已转换为data URI")
                else:
                    url = file_path

                # 调用create_voice方法复刻声音
                voice_id = self.service.create_voice(
                    target_model=self.target_model,
                    prefix=custom_prefix,
                    url=url
                )

                print(f"  √ 成功创建音色，ID: {voice_id}")
                results[name] = voice_id

                # 避免频繁请求触发限流
                if i < total:
                    time.sleep(1)

            except Exception as e:
                print(f"  × 克隆失败: {name}, 错误: {str(e)}")

        print(f"批量克隆完成，成功: {len(results)}/{total}")
        return results

    def test_voices(self, voice_ids: Dict[str, str], test_text: str, output_dir: str = "outputs") -> None:
        """
        测试克隆的声音，生成测试音频

        Args:
            voice_ids: 字典，键为音频标识名，值为voice_id
            test_text: 用于测试的文本
            output_dir: 输出目录
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        print(f"开始测试 {len(voice_ids)} 个克隆声音...")
        total = len(voice_ids)

        for i, (name, voice_id) in enumerate(voice_ids.items(), 1):
            try:
                print(f"[{i}/{total}] 测试音色: {name}")

                # 创建语音合成器
                synthesizer = SpeechSynthesizer(model=self.target_model, voice=voice_id)

                # 合成语音
                audio = synthesizer.call(test_text)

                # 保存音频文件
                output_path = os.path.join(output_dir, f"{name}.mp3")
                with open(output_path, "wb") as f:
                    f.write(audio)

                print(f"  √ 已保存测试音频: {output_path}")

                # 避免频繁请求触发限流
                if i < total:
                    time.sleep(1)

            except Exception as e:
                print(f"  × 测试失败: {name}, 错误: {str(e)}")

    def list_all_voices(self, prefix: str = None) -> List[dict]:
        """
        获取所有已克隆的声音列表

        Args:
            prefix: 筛选特定前缀的声音，不指定则返回所有

        Returns:
            声音列表
        """
        all_voices = []
        page_index = 0
        page_size = 100

        while True:
            voices = self.service.list_voices(prefix=prefix, page_index=page_index, page_size=page_size)
            if not voices:
                break

            all_voices.extend(voices)
            page_index += 1

            # 如果返回的数量小于页大小，说明已经是最后一页
            if len(voices) < page_size:
                break

        return all_voices

    def delete_voices(self, voice_ids: List[str]) -> None:
        """
        批量删除克隆的声音

        Args:
            voice_ids: 要删除的voice_id列表
        """
        total = len(voice_ids)
        print(f"开始批量删除 {total} 个声音...")

        for i, voice_id in enumerate(voice_ids, 1):
            try:
                print(f"[{i}/{total}] 删除音色: {voice_id}")
                self.service.delete_voice(voice_id)
                print(f"  √ 成功删除")

                # 避免频繁请求触发限流
                if i < total:
                    time.sleep(0.5)

            except Exception as e:
                print(f"  × 删除失败: {voice_id}, 错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量语音克隆工具")
    parser.add_argument("--api_key", help="DashScope API密钥，可选，默认从环境变量DASHSCOPE_API_KEY获取")
    parser.add_argument("--input_file", help="输入文件路径，CSV格式，包含name,file_path两列")
    parser.add_argument("--prefix", default="batch", help="音色前缀，默认为batch")
    parser.add_argument("--test_text", default="Hey Memo, take a picture of this and then volume up. Play the next music and then stop recording.", help="测试文本")
    parser.add_argument("--output_dir", default="voice_outputs", help="输出目录")
    parser.add_argument("--use_local", action="store_true", help="使用本地音频文件而不是URL")
    parser.add_argument("--list", action="store_true", help="列出所有已克隆的声音")
    parser.add_argument("--list_prefix", help="列出指定前缀的声音")
    parser.add_argument("--audio_dir", help="本地音频文件目录，将处理该目录下所有支持的音频文件")

    args = parser.parse_args()

    # 创建批量克隆工具实例
    cloner = BatchVoiceCloner(api_key="sk-995d8d12b06246fabb433fc1b4269e20")

    # 列出所有声音
    if args.list or args.list_prefix:
        voices = cloner.list_all_voices(prefix=args.list_prefix)
        print(f"共找到 {len(voices)} 个音色:")
        for voice in voices:
            print(f"ID: {voice['voice_id']}, 创建时间: {voice['gmt_create']}, 状态: {voice['status']}")
        return

    # 从音频目录批量处理
    if args.audio_dir:
        if not os.path.isdir(args.audio_dir):
            print(f"错误: 指定的目录不存在: {args.audio_dir}")
            return

        audio_files = {}
        # 支持的音频格式
        valid_extensions = ['.wav', '.mp3', '.m4a']

        # 遍历目录下的所有文件
        for filename in os.listdir(args.audio_dir):
            _, ext = os.path.splitext(filename)
            if ext.lower() in valid_extensions:
                # 使用文件名作为音色标识名
                name = os.path.splitext(filename)[0]
                file_path = os.path.join(args.audio_dir, filename)
                audio_files[name] = file_path

        if not audio_files:
            print(f"错误: 在目录 {args.audio_dir} 中未找到支持的音频文件")
            return

        print(f"发现 {len(audio_files)} 个音频文件")

        # 执行批量克隆
        voice_ids = cloner.clone_voices(audio_files, prefix=args.prefix, use_local_files=True)

        # 保存克隆结果并测试
        save_and_test_results(cloner, voice_ids, args.test_text, args.output_dir)
        return

    # 从输入文件批量克隆
    if args.input_file:
        # 读取输入文件
        audio_files = {}
        with open(args.input_file, 'r', encoding='utf-8') as f:
            # 跳过标题行
            header = next(f).strip().split(',')
            file_column = 'file_path' if 'file_path' in header else 'url'
            file_index = header.index(file_column)
            name_index = header.index('name') if 'name' in header else 0

            for line in f:
                parts = line.strip().split(',')
                if len(parts) > max(name_index, file_index):
                    name = parts[name_index]
                    file_path = parts[file_index]
                    audio_files[name] = file_path

        if not audio_files:
            print("错误: 输入文件为空或格式不正确")
            return

        # 执行批量克隆
        voice_ids = cloner.clone_voices(audio_files, prefix=args.prefix, use_local_files=args.use_local)

        # 保存克隆结果并测试
        save_and_test_results(cloner, voice_ids, args.test_text, args.output_dir)
    else:
        print("请提供输入文件路径(--input_file)或音频目录(--audio_dir)")


def save_and_test_results(cloner, voice_ids, test_text, output_dir):
    """保存克隆结果并测试音色"""
    # 保存克隆结果
    result_file = os.path.join(output_dir, "clone_results.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write("name,voice_id\n")
        for name, voice_id in voice_ids.items():
            f.write(f"{name},{voice_id}\n")

    print(f"克隆结果已保存到: {result_file}")

    # 测试克隆的声音
    cloner.test_voices(voice_ids, test_text, output_dir)


if __name__ == "__main__":
    main()
