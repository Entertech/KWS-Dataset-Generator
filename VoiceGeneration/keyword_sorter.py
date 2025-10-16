import os
import re
import shutil
import logging

# --- 配置 ---
SOURCE_DIR = r"F:/1.6s_half_augment"  # 输入的根目录，脚本将递归搜索此目录下的所有 .wav
OUTPUT_ROOT = r"F:/half_augment"  # 输出根目录，脚本会在此目录下按关键词创建子文件夹
KEYWORDS = [
    "HeyMemo",
    "LookAnd",
    "Next",
    "Pause",
    "Play",
    "StopRecording",
    "TakeAPicture",
    "TakeAVideo",
    "VolumeUp",
    "VolumeDown"
]
# 是否从同名 .txt 文件中读取文本参与匹配（如：xxx.wav 对应 xxx.txt）
USE_SIDE_CAR_TXT = True
# --- 配置结束 ---

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def normalize(s: str) -> str:
    """规范化字符串：去除非字母数字，全部转小写"""
    return re.sub(r"[^a-z0-9]", "", s.lower())

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def safe_copy(src: str, dest_dir: str):
    """复制文件到目标目录，若存在同名文件则添加序号后缀避免覆盖"""
    ensure_dir(dest_dir)
    base = os.path.basename(src)
    name, ext = os.path.splitext(base)
    dest_path = os.path.join(dest_dir, base)
    if not os.path.exists(dest_path):
        shutil.copy2(src, dest_path)
        return dest_path
    # 存在同名，添加后缀
    idx = 1
    while True:
        new_name = f"{name}_copy{idx}{ext}"
        dest_path = os.path.join(dest_dir, new_name)
        if not os.path.exists(dest_path):
            shutil.copy2(src, dest_path)
            return dest_path
        idx += 1

def collect_candidates(file_path: str) -> list[str]:
    """收集用于匹配的候选文本：文件名、父目录名、同名txt内容（可选）"""
    candidates = []
    base = os.path.basename(file_path)
    name_no_ext, _ = os.path.splitext(base)
    candidates.append(name_no_ext)
    # 父目录名
    parent_name = os.path.basename(os.path.dirname(file_path))
    if parent_name:
        candidates.append(parent_name)
    # 同名 txt 内容
    if USE_SIDE_CAR_TXT:
        txt_path = os.path.splitext(file_path)[0] + ".txt"
        if os.path.isfile(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if content:
                        candidates.append(content)
            except Exception as e:
                logging.warning(f"读取文本失败: {txt_path}, {e}")
    return candidates

def match_keywords(candidates: list[str], keywords: list[str]) -> list[str]:
    """对候选文本进行规范化后，返回匹配到的关键词列表"""
    norm_candidates = [normalize(c) for c in candidates if isinstance(c, str)]
    matched = []
    for kw in keywords:
        norm_kw = normalize(kw)
        for nc in norm_candidates:
            if norm_kw in nc:
                matched.append(kw)
                break
    return matched

def sort_wavs_by_keyword(source_dir: str, output_root: str, keywords: list[str]):
    logging.info(f"开始扫描: {source_dir}")
    total_files = 0
    matched_files = 0
    unknown_files = 0
    multi_match_files = 0

    ensure_dir(output_root)
    unknown_dir = os.path.join(output_root, "Unknown")
    ambiguous_dir = os.path.join(output_root, "Ambiguous")  # 可选：多关键词匹配时也复制到此汇总目录
    ensure_dir(unknown_dir)
    ensure_dir(ambiguous_dir)

    for root, _, files in os.walk(source_dir):
        for f in files:
            if not f.lower().endswith(".wav"):
                continue
            total_files += 1
            wav_path = os.path.join(root, f)
            candidates = collect_candidates(wav_path)
            hits = match_keywords(candidates, keywords)

            if not hits:
                # 未匹配，复制到 Unknown
                copied = safe_copy(wav_path, unknown_dir)
                unknown_files += 1
                logging.info(f"未匹配 -> Unknown: {copied}")
                continue

            # 多关键词匹配：复制到每个关键词子目录，同时也复制到 Ambiguous（便于人工复核）
            if len(hits) > 1:
                multi_match_files += 1
                for kw in hits:
                    dest_dir = os.path.join(output_root, kw)
                    copied = safe_copy(wav_path, dest_dir)
                    logging.info(f"多匹配({hits}) -> {kw}: {copied}")
                copied = safe_copy(wav_path, ambiguous_dir)
                continue

            # 单关键词匹配：复制到对应关键词目录
            matched_files += 1
            kw = hits[0]
            dest_dir = os.path.join(output_root, kw)
            copied = safe_copy(wav_path, dest_dir)
            logging.info(f"匹配 -> {kw}: {copied}")

    logging.info(f"扫描完成。总数: {total_files}, 单匹配: {matched_files}, 多匹配: {multi_match_files}, 未匹配: {unknown_files}")
    logging.info(f"结果目录: {output_root}")

if __name__ == "__main__":
    sort_wavs_by_keyword(SOURCE_DIR, OUTPUT_ROOT, KEYWORDS)