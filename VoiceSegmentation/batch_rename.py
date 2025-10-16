import os
import re


def get_unique_file_path(file_path):
    """
    如果文件已存在，生成一个唯一的文件路径
    """
    base, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(file_path):
        file_path = f"{base}_{counter}{ext}"
        counter += 1
    return file_path


def batch_rename_files(root_dir, word_replacements, file_extensions=None, exclude_folders=True):
    """
    批量重命名文件，将文件名中的指定词替换成另一个词
    
    Args:
        root_dir (str): 要遍历的根目录
        word_replacements (list): 替换规则列表，格式为 [{'old': '旧词', 'new': '新词'}, ...]
        file_extensions (list): 要处理的文件扩展名列表，如 ['.txt', '.wav']，None表示处理所有文件
        exclude_folders (bool): 是否排除文件夹名，默认True（只处理文件名）
    
    Returns:
        int: 重命名的文件数量
    """
    renamed_count = 0
    
    if not os.path.exists(root_dir):
        print(f"错误：目录 '{root_dir}' 不存在")
        return 0
    
    print(f"开始遍历目录: {root_dir}")
    print(f"替换规则: {word_replacements}")
    print(f"文件类型过滤: {file_extensions if file_extensions else '所有文件'}")
    print("-" * 50)
    
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            # 检查文件扩展名
            if file_extensions:
                if not any(filename.lower().endswith(ext.lower()) for ext in file_extensions):
                    continue
            
            old_file_path = os.path.join(root, filename)
            new_filename = filename
            
            # 应用所有替换规则
            for replacement in word_replacements:
                old_word = replacement['old']
                new_word = replacement['new']
                new_filename = new_filename.replace(old_word, new_word)
            
            # 如果文件名发生了变化，进行重命名
            if new_filename != filename:
                new_file_path = os.path.join(root, new_filename)
                
                # 确保新文件名唯一
                unique_path = get_unique_file_path(new_file_path)
                
                try:
                    os.rename(old_file_path, unique_path)
                    print(f"✓ 重命名: {filename} -> {os.path.basename(unique_path)}")
                    print(f"  路径: {root}")
                    renamed_count += 1
                except Exception as e:
                    print(f"✗ 重命名失败 {filename}: {e}")
    
    return renamed_count


def batch_rename_files_regex(root_dir, regex_replacements, file_extensions=None, exclude_folders=True):
    """
    使用正则表达式批量重命名文件
    
    Args:
        root_dir (str): 要遍历的根目录
        regex_replacements (list): 正则替换规则列表，格式为 [{'pattern': '正则模式', 'replacement': '替换内容'}, ...]
        file_extensions (list): 要处理的文件扩展名列表，如 ['.txt', '.wav']，None表示处理所有文件
        exclude_folders (bool): 是否排除文件夹名，默认True（只处理文件名）
    
    Returns:
        int: 重命名的文件数量
    """
    renamed_count = 0
    
    if not os.path.exists(root_dir):
        print(f"错误：目录 '{root_dir}' 不存在")
        return 0
    
    print(f"开始遍历目录: {root_dir}")
    print(f"正则替换规则: {regex_replacements}")
    print(f"文件类型过滤: {file_extensions if file_extensions else '所有文件'}")
    print("-" * 50)
    
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            # 检查文件扩展名
            if file_extensions:
                if not any(filename.lower().endswith(ext.lower()) for ext in file_extensions):
                    continue
            
            old_file_path = os.path.join(root, filename)
            new_filename = filename
            
            # 应用所有正则替换规则
            for replacement in regex_replacements:
                pattern = replacement['pattern']
                repl = replacement['replacement']
                new_filename = re.sub(pattern, repl, new_filename)
            
            # 如果文件名发生了变化，进行重命名
            if new_filename != filename:
                new_file_path = os.path.join(root, new_filename)
                
                # 确保新文件名唯一
                unique_path = get_unique_file_path(new_file_path)
                
                try:
                    os.rename(old_file_path, unique_path)
                    print(f"✓ 重命名: {filename} -> {os.path.basename(unique_path)}")
                    print(f"  路径: {root}")
                    renamed_count += 1
                except Exception as e:
                    print(f"✗ 重命名失败 {filename}: {e}")
    
    return renamed_count


def remove_words_from_filenames(root_dir, words_to_remove, file_extensions=None):
    """
    从文件名中删除指定的词汇
    
    Args:
        root_dir (str): 要遍历的根目录
        words_to_remove (list): 要删除的词汇列表
        file_extensions (list): 要处理的文件扩展名列表，None表示处理所有文件
    
    Returns:
        int: 重命名的文件数量
    """
    # 将删除操作转换为替换操作（替换为空字符串）
    word_replacements = [{'old': word, 'new': ''} for word in words_to_remove]
    return batch_rename_files(root_dir, word_replacements, file_extensions)


if __name__ == "__main__":
    # 配置区域 - 请根据需要修改以下参数
    
    # 1. 设置要处理的目录
    root_directory = "D:/LooktechVoice/VoiceGeneration/edgetts_generated_new"  # 修改为你的目录路径
    
    # 2. 选择处理模式（取消注释你需要的模式）
    
    # 模式1: 简单词汇替换
    word_replacements = [
        {'old': 'Pause Music', 'new': 'PauseMusic'},
        {'old': 'Play Music', 'new': 'PlayMusic'},
        {'old': 'Start Recording', 'new': 'StartRecording'},
    ]
    
    # 模式2: 删除指定词汇（取消注释使用）
    # words_to_remove = ['temp', 'test', '临时', 'backup']
    
    # 模式3: 正则表达式替换（取消注释使用）
    # regex_replacements = [
    #     {'pattern': r'\d{4}-\d{2}-\d{2}', 'replacement': 'DATE'},  # 将日期格式替换为DATE
    #     {'pattern': r'[Tt]est', 'replacement': 'TEST'},  # 将test或Test替换为TEST
    #     {'pattern': r'\s+', 'replacement': '_'},  # 将多个空格替换为下划线
    #     {'pattern': r'[\(\)]', 'replacement': ''}  # 删除括号
    # ]
    
    # 3. 设置文件类型过滤（None表示处理所有文件）
    file_extensions = ['.wav', '.mp3', '.txt']  # 只处理这些类型的文件
    # file_extensions = None  # 处理所有文件
    
    # 4. 执行重命名操作
    print("=" * 60)
    print("批量文件重命名工具")
    print("=" * 60)
    
    # 执行模式1: 词汇替换
    renamed_count = batch_rename_files(
        root_directory, 
        word_replacements, 
        file_extensions
    )
    
    # 执行模式2: 删除词汇（取消注释使用）
    # renamed_count = remove_words_from_filenames(
    #     root_directory,
    #     words_to_remove,
    #     file_extensions
    # )
    
    # 执行模式3: 正则表达式替换（取消注释使用）
    # renamed_count = batch_rename_files_regex(
    #     root_directory,
    #     regex_replacements,
    #     file_extensions
    # )
    
    print("-" * 50)
    print(f"批量重命名完成！共重命名了 {renamed_count} 个文件")
    
    if renamed_count == 0:
        print("提示：没有找到需要重命名的文件，请检查：")
        print("1. 目录路径是否正确")
        print("2. 文件扩展名过滤是否正确")
        print("3. 替换规则是否匹配现有文件名")
        