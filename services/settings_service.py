import json
import os
from typing import Dict, Any
from datetime import datetime

SETTINGS_FILE = "feed_settings.json"

class SettingsService:
    def __init__(self):
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """설정 파일에서 설정을 불러옵니다."""
        default_settings = {
            "mode": "manual",  # manual 또는 auto
            "interval": 60,    # 분 단위
            "amount": 1        # 한번에 주는 양
        }
        
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # 기본값과 병합
                    default_settings.update(loaded_settings)
                    print(f"📂 설정 파일 로드됨: {loaded_settings}")
            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패: {e}")
        
        return default_settings
    
    def save_settings(self) -> bool:
        """현재 설정을 파일에 저장합니다."""
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print(f"💾 설정 저장됨: {self.settings}")
            return True
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            return False
    
    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        """새로운 설정을 받아서 업데이트합니다."""
        # 유효성 검사
        if "mode" in new_settings:
            if new_settings["mode"] not in ["manual", "auto"]:
                raise ValueError("mode는 'manual' 또는 'auto'여야 합니다")
        
        if "interval" in new_settings:
            interval = int(new_settings["interval"])
            if interval < 1 or interval > 1440:  # 1분~24시간
                raise ValueError("interval은 1~1440 사이의 값이어야 합니다")
            new_settings["interval"] = interval
        
        if "amount" in new_settings:
            amount = int(new_settings["amount"])
            if amount < 1 or amount > 10:  # 1~10회
                raise ValueError("amount는 1~10 사이의 값이어야 합니다")
            new_settings["amount"] = amount
        
        # 설정 업데이트
        self.settings.update(new_settings)
        
        # 파일에 저장
        self.save_settings()
        
        print(f"🔧 설정 업데이트됨: {self.settings}")
        return self.settings
    
    def get_settings(self) -> Dict[str, Any]:
        """현재 설정을 반환합니다."""
        return self.settings.copy()
    
    def get_setting(self, key: str) -> Any:
        """특정 설정값을 반환합니다."""
        return self.settings.get(key)

# 전역 인스턴스
settings_service = SettingsService() 