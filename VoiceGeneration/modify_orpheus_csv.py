import pandas as pd
import numpy as np
import random


def modify_csv(input_file, output_file):
    """
    修改CSV文件，添加voice、top_p、temperature和repetition_penalty列

    参数:
    input_file: 输入CSV文件路径
    output_file: 输出CSV文件路径
    """
    # 读取CSV文件
    try:
        df = pd.read_csv(input_file)
        print(f"成功读取CSV文件，共{len(df)}行")
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return False

    # 设置随机种子确保可重现性
    np.random.seed(42)

    # 添加voice列 - 根据gender选择
    def assign_voice(gender):
        if gender.lower() == 'female':
            return np.random.choice(['tara', 'emma'])
        else:  # 假设其他都是male
            return np.random.choice(['dan', 'josh'])

    df['voice'] = df['gender'].apply(assign_voice)

    # 添加top_p列 - 随机值在0.9~1.0之间
    df['top_p'] = np.random.uniform(0.9, 1.0, len(df)).round(2)

    # 添加temperature列 - 随机值在0.5~0.7之间
    df['temperature'] = np.random.uniform(0.5, 0.7, len(df)).round(2)

    # 添加repetition_penalty列 - 随机值在1.1~1.5之间
    df['repetition_penalty'] = np.random.uniform(1.1, 1.5, len(df)).round(2)

    # 保存修改后的CSV文件
    try:
        df.to_csv(output_file, index=False)
        print(f"已成功保存修改后的CSV文件: {output_file}")
        print(f"新增列: voice, top_p, temperature, repetition_penalty")

        # 显示一些统计信息
        print("\n数据统计:")
        print(f"女性声音分布: {df[df['gender'] == 'Female']['voice'].value_counts(normalize=True).round(2)}")
        print(f"男性声音分布: {df[df['gender'] == 'Male']['voice'].value_counts(normalize=True).round(2)}")
        print(f"top_p范围: {df['top_p'].min()} - {df['top_p'].max()}")
        print(f"temperature范围: {df['temperature'].min()} - {df['temperature'].max()}")
        print(f"repetition_penalty范围: {df['repetition_penalty'].min()} - {df['repetition_penalty'].max()}")

        return True
    except Exception as e:
        print(f"保存CSV文件失败: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    input_file = "sample_1.csv"  # 输入文件名
    output_file = "sample_1_modified.csv"  # 输出文件名

    success = modify_csv(input_file, output_file)
    if success:
        print("CSV文件修改完成！")
    else:
        print("CSV文件修改失败！")
