# services/feed_setting.py
from services.settings_service import settings_service

# 기존 코드와의 호환성을 위한 별칭
feed_config = settings_service.settings

def update_settings(new_settings: dict):
    """기존 코드와의 호환성을 위한 함수"""
    return settings_service.update_settings(new_settings)
