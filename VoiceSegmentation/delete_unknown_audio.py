import os
import glob
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('delete_unknown')

def delete_unknown_audio_files(root_directory, dry_run=True):
    """
    删除所有文件名包含'Unknown'的音频文件
    
    Args:
        root_directory (str): 要搜索的根目录
        dry_run (bool): 如果为True，只显示要删除的文件而不实际删除
    
    Returns:
        tuple: (删除的文件数量, 删除的文件列表)
    """
    
    # 支持的音频格式
    audio_extensions = ['*.wav', '*.mp3', '*.m4a', '*.flac', '*.aac']
    
    deleted_files = []
    deleted_count = 0
    
    logger.info(f"开始搜索目录: {root_directory}")
    logger.info(f"模式: {'预览模式（不实际删除）' if dry_run else '删除模式'}")
    
    # 递归搜索所有音频文件
    for extension in audio_extensions:
        pattern = os.path.join(root_directory, '**', extension)
        files = glob.glob(pattern, recursive=True)
        
        for file_path in files:
            filename = os.path.basename(file_path)
            
            # 检查文件名是否包含'Unknown'（不区分大小写）
            if 'unknown' in filename.lower():
                if dry_run:
                    logger.info(f"[预览] 将删除: {file_path}")
                else:
                    try:
                        os.remove(file_path)
                        logger.info(f"[已删除] {file_path}")
                    except Exception as e:
                        logger.error(f"删除失败 {file_path}: {str(e)}")
                        continue
                
                deleted_files.append(file_path)
                deleted_count += 1
    
    return deleted_count, deleted_files

def main():
    """主函数"""
    
    # 配置区域 - 请根据需要修改这些设置
    ROOT_DIRECTORY = "D:/LooktechVoice/results_orpheus_new"  # 要搜索的根目录
    DRY_RUN = False  # 设置为False来实际删除文件
    
    print("=" * 60)
    print("删除包含'Unknown'的音频文件工具")
    print("=" * 60)
    print(f"搜索目录: {ROOT_DIRECTORY}")
    print(f"运行模式: {'预览模式（安全）' if DRY_RUN else '删除模式（危险）'}")
    print("=" * 60)
    
    # 检查目录是否存在
    if not os.path.exists(ROOT_DIRECTORY):
        logger.error(f"目录不存在: {ROOT_DIRECTORY}")
        return
    
    # 执行删除操作
    try:
        count, files = delete_unknown_audio_files(ROOT_DIRECTORY, DRY_RUN)
        
        print("\n" + "=" * 60)
        print("操作完成")
        print("=" * 60)
        print(f"找到的文件数量: {count}")
        
        if DRY_RUN:
            print("\n注意: 这是预览模式，没有实际删除文件")
            print("如需实际删除，请将 DRY_RUN 设置为 False")
        else:
            print(f"\n实际删除的文件数量: {count}")
        
        # 显示文件列表（如果数量不太多）
        if count > 0 and count <= 20:
            print("\n文件列表:")
            for file_path in files:
                print(f"  - {file_path}")
        elif count > 20:
            print(f"\n文件数量较多({count}个)，已省略详细列表")
            
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")

if __name__ == "__main__":
    main()