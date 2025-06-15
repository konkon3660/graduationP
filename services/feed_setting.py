# services/feed_settings.py

feed_config = {
    "mode": "manual",  # 또는 "auto"
    "interval": 60,     # 분 단위
    "amount": 1         # 한번에 주는 양
}

def update_settings(new_settings: dict):
    feed_config.update(new_settings)
    print(f"🔧 급식 설정 업데이트됨: {feed_config}")
