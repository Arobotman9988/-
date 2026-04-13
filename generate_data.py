import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

# ============ 核心配置 ============
LANGUAGES = ['English', 'Chinese', 'Spanish', 'Japanese', 'Korean', 'French',
             'German', 'Portuguese', 'Russian', 'Arabic', 'Italian', 'Dutch']
COUNTRIES = ['USA', 'China', 'Japan', 'South Korea', 'Spain', 'France',
             'Germany', 'Brazil', 'UK', 'Canada', 'Australia', 'Mexico']
USER_TYPES = ['free', 'premium']

# 时间范围：过去 12 个月
START_DATE = datetime(2025, 4, 12)
END_DATE = datetime(2026, 4, 12)

def generate_users(n_users=10000):
    """生成用户基础信息"""
    print(f"📊 正在生成 {n_users} 名用户数据...")

    users = []
    for i in range(n_users):
        reg_date = START_DATE + timedelta(days=random.randint(0, 365))
        native_lang = random.choice(LANGUAGES)
        target_langs = random.sample([l for l in LANGUAGES if l != native_lang],
                                     k=random.randint(1, 3))

        user = {
            'user_id': f'HT_{i+10000:06d}',
            'register_date': reg_date,
            'country': random.choice(COUNTRIES),
            'native_language': native_lang,
            'target_languages': '|'.join(target_langs),
            'user_type': random.choices(USER_TYPES, weights=[85, 15])[0],
            'age_group': random.choices(['18-24', '25-34', '35-44', '45+'],
                                        weights=[35, 40, 18, 7])[0],
            'gender': random.choice(['M', 'F', 'Other']),
            'learning_goal': random.choice(['Travel', 'Business', 'Exam', 'Hobby', 'Immigration'])
        }
        users.append(user)

    return pd.DataFrame(users)

def generate_language_pairs(users_df, n_pairs=50000):
    """生成语言配对记录"""
    print(f"💬 正在生成 {n_pairs} 条语言配对数据...")

    pairs = []
    user_ids = users_df['user_id'].tolist()

    for _ in range(n_pairs):
        user_a = random.choice(user_ids)
        user_b = random.choice([u for u in user_ids if u != user_a])

        pair_date = START_DATE + timedelta(days=random.randint(0, 365))
        match_success = random.choices([0, 1], weights=[60, 40])[0]

        pair = {
            'pair_id': f'PAIR_{len(pairs)+1:06d}',
            'user_a_id': user_a,
            'user_b_id': user_b,
            'pair_date': pair_date,
            'match_success': match_success,
            'response_time_hours': round(np.random.exponential(2), 2) if match_success else None,
            'conversation_duration_min': round(np.random.gamma(shape=2, scale=15), 2) if match_success else None,
            'messages_exchanged': int(np.random.poisson(8)) if match_success else 0,
            'pair_rating': random.randint(3, 5) if match_success and random.random() > 0.3 else None
        }
        pairs.append(pair)

    return pd.DataFrame(pairs)

def generate_user_activity(users_df, n_records=200000):
    """生成用户活跃度数据"""
    print(f"⚡ 正在生成 {n_records} 条用户行为数据...")

    activities = []
    activity_types = ['login', 'send_message', 'voice_call', 'video_call',
                      'post_moment', 'comment', 'like', 'share_content',
                      'start_lesson', 'complete_lesson']

    for _, user in users_df.iterrows():
        # 每个用户生成多条活动记录
        n_activities = random.randint(5, 50)
        for _ in range(n_activities):
            days_since_reg = min((END_DATE - user['register_date']).days, 365)
            if days_since_reg <= 0:
                continue

            activity_date = user['register_date'] + timedelta(
                days=random.randint(0, max(0, days_since_reg))
            )

            act_type = random.choices(activity_types,
                                      weights=[30, 20, 8, 5, 10, 8, 12, 4, 2, 1])[0]

            activities.append({
                'user_id': user['user_id'],
                'activity_date': activity_date,
                'activity_type': act_type,
                'session_duration_min': round(max(0.5, np.random.exponential(10)), 2),
                'device_type': random.choices(['iOS', 'Android', 'Web'], weights=[45, 48, 7])[0]
            })

    return pd.DataFrame(activities[:n_records])

def generate_subscription_data(users_df):
    """生成订阅转化数据"""
    print("💰 正在生成订阅转化数据...")

    subscriptions = []
    free_users = users_df[users_df['user_type'] == 'free']

    for _, user in free_users.iterrows():
        if random.random() < 0.12:  # 12% 转化率
            trial_start = user['register_date'] + timedelta(days=random.randint(1, 30))
            converted = random.choices([0, 1], weights=[35, 65])[0]

            sub_record = {
                'user_id': user['user_id'],
                'trial_start_date': trial_start,
                'trial_end_date': trial_start + timedelta(days=7),
                'converted_to_premium': converted,
                'conversion_day': (trial_start + timedelta(days=random.randint(1, 7))).date()
                                   if converted else None,
                'subscription_plan': random.choice(['Monthly', 'Quarterly', 'Yearly']) if converted else None,
                'initial_payment_usd': random.choice([9.99, 24.99, 69.99]) if converted else 0
            }
            subscriptions.append(sub_record)

    return pd.DataFrame(subscriptions)

def generate_retention_cohorts(users_df, activity_df):
    """生成留存率队列数据"""
    print("📈 正在计算留存率队列...")

    # 按注册月份分组
    users_df['cohort'] = users_df['register_date'].dt.to_period('M')

    # 计算每周活跃情况
    retention_data = []

    for cohort, cohort_users in users_df.groupby('cohort'):
        cohort_user_ids = set(cohort_users['user_id'])

        for week in range(13):  # 13 周
            week_start = cohort.start_time + timedelta(weeks=week)
            week_end = week_start + timedelta(weeks=1)

            week_activity = activity_df[
                (activity_df['user_id'].isin(cohort_user_ids)) &
                (activity_df['activity_date'] >= week_start) &
                (activity_df['activity_date'] < week_end)
            ]['user_id'].nunique()

            retention_data.append({
                'cohort': str(cohort),
                'week': week,
                'active_users': week_activity,
                'total_users': len(cohort_user_ids),
                'retention_rate': week_activity / len(cohort_user_ids)
            })

    return pd.DataFrame(retention_data)

def main():
    print("=" * 60)
    print("🚀 数据分析项目 - 数据生成器")
    print("=" * 60)

    # 生成各类数据
    users_df = generate_users(10000)
    pairs_df = generate_language_pairs(users_df, 50000)
    activity_df = generate_user_activity(users_df, 200000)
    subscription_df = generate_subscription_data(users_df)
    retention_df = generate_retention_cohorts(users_df, activity_df)

    # 保存数据
    print("\n💾 正在保存数据文件...")
    users_df.to_csv('data/users.csv', index=False)
    pairs_df.to_csv('data/language_pairs.csv', index=False)
    activity_df.to_csv('data/user_activity.csv', index=False)
    subscription_df.to_csv('data/subscriptions.csv', index=False)
    retention_df.to_csv('data/retention_cohorts.csv', index=False)

    print("\n✅ 数据生成完成！")
    print(f"   👥 用户数: {len(users_df):,}")
    print(f"   💬 配对数: {len(pairs_df):,}")
    print(f"   ⚡ 行为记录: {len(activity_df):,}")
    print(f"   💰 订阅转化: {len(subscription_df):,}")
    print(f"   📊 留存队列: {len(retention_df):,}")

if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    main()
