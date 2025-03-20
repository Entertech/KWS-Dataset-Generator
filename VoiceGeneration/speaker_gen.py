import numpy as np
import pandas as pd


def generate_target(n_samples=1000):
    """
    参数:
    n_samples: 生成样本的数量
    seed: 随机种子，确保结果可重现

    返回:
    pandas DataFrame 包含生成的样本和特征
    """
    np.random.seed()
    # 定义城市、口音和百分比
    cities_data = {
        "Los Angeles": {"country": "USA", "accent": "Westcoast US", "percent": 30},
        "New York": {"country": "USA", "accent": "Eastcoast US", "percent": 25},
        "Chicago": {"country": "USA", "accent": "Midwest US", "percent": 10},
        "Dallas": {"country": "USA", "accent": "South US", "percent": 5},
        "Miami": {"country": "USA", "accent": "Latin", "percent": 10},
        "Montreal": {"country": "CA", "accent": "French", "percent": 5},
        "London": {"country": "UK", "accent": "England", "percent": 10},
        "Delhi": {"country": "IND", "accent": "India", "percent": 3},
        "Sydney": {"country": "AUS", "accent": "Australia", "percent": 2}
    }

    # 从城市分布中抽样
    cities = list(cities_data.keys())
    probabilities = [cities_data[city]["percent"] / 100 for city in cities]

    # 生成城市样本
    sampled_cities = np.random.choice(cities, size=n_samples, p=probabilities)

    # 生成国家样本（根据城市）
    countries = [cities_data[city]["country"] for city in sampled_cities]

    # 生成口音样本（根据城市）
    accents = [cities_data[city]["accent"] for city in sampled_cities]

    # 生成性别样本（1:1比例）
    genders = np.random.choice(["Male", "Female"], size=n_samples, p=[0.5, 0.5])

    # 生成年龄样本（15-80岁，中位数35）
    age_ranges = {
        (15, 24): 18,
        (25, 34): 30,
        (35, 44): 22,
        (45, 54): 15,
        (55, 64): 10,
        (65, 80): 5
    }
    ages = []
    age_groups = list(age_ranges.keys())
    age_probs = [age_ranges[group] / 100 for group in age_groups]
    selected_ranges = np.random.choice(len(age_groups), size=n_samples, p=age_probs)
    for i in range(n_samples):
        min_age, max_age = age_groups[selected_ranges[i]]
        ages.append(np.random.randint(min_age, max_age + 1))
    ages = np.array(ages)

    # 生成语速样本 (Fast 20%, Normal 60%, Slow 20%)
    speech_rates = np.random.choice(["Fast", "Normal", "Slow"], size=n_samples, p=[0.2, 0.6, 0.2])

    # 创建基本标识符
    base_identifiers = [f"{country}_{city}_{gender}_{age}_{rate}"
                        for country, city, gender, age, rate in
                        zip(countries, sampled_cities, genders, ages, speech_rates)]

    # 检查并处理重复项
    unique_identifiers = []
    id_count = {}

    for base_id in base_identifiers:
        if base_id in id_count:
            id_count[base_id] += 1
            # 为重复项添加后缀
            unique_id = f"{base_id}_{id_count[base_id]}"
        else:
            id_count[base_id] = 0
            unique_id = base_id

        unique_identifiers.append(unique_id)

    # 创建DataFrame
    df = pd.DataFrame({
        "identifier": unique_identifiers,
        "country": countries,
        "city": sampled_cities,
        "accent": accents,
        "gender": genders,
        "age": ages,
        "speech_rate": speech_rates
    })
    return df


# 示例用法
if __name__ == "__main__":
    samples = generate_target(300)
    csv_filename = "sample.csv"
    samples.to_csv(csv_filename, index=False, encoding='utf-8')

    # 验证分布
    print("\n城市分布:")
    city_distribution = samples["city"].value_counts(normalize=True) * 100
    print(city_distribution)

    print("\n性别分布:")
    gender_distribution = samples["gender"].value_counts(normalize=True) * 100
    print(gender_distribution)

    print("\n语速分布:")
    rate_distribution = samples["speech_rate"].value_counts(normalize=True) * 100
    print(rate_distribution)

    print("\n年龄统计:")
    print(f"年龄范围: {samples['age'].min()}-{samples['age'].max()}")
    print(f"年龄中位数: {samples['age'].median()}")
    print(f"年龄平均值: {samples['age'].mean():.1f}")

    # 检查唯一性
    print(f"\n总样本数: {len(samples)}")
    print(f"唯一标识符数: {len(samples['identifier'].unique())}")
    print(f"是否有重复标识符: {len(samples) > len(samples['identifier'].unique())}")

    # 如果有重复，打印重复项
    if len(samples) > len(samples['identifier'].unique()):
        duplicates = samples[samples.duplicated(subset=['identifier'], keep=False)]
        print("\n重复的标识符:")
        print(duplicates['identifier'].value_counts())
