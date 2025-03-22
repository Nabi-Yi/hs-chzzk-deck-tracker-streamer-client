import requests
import json
import os
import threading
from dotenv import load_dotenv



class LogApiSender:
    def __init__(self, api_url=None, api_key=None):
        """
        API 전송 클래스 초기화
        
        Args:
            api_url (str): API 엔드포인트 URL
            api_key (str): API 인증 키
        """
        self.api_url = os.getenv("API_URL")
        self.api_key = None
        self.headers = None
        print(self.api_url)
    
    def set_api_key(self, api_key):
        """API 키 설정"""
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _send_log_data_thread(self, log_data):
        """
        별도 스레드에서 로그 데이터를 API로 전송하는 함수
        
        Args:
            log_data (dict): 전송할 로그 데이터
        """
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(log_data)
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.text else None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def send_log_data(self, log_data):
        """
        로그 데이터를 API로 전송 (비동기 처리)
        
        Args:
            log_data (dict): 전송할 로그 데이터
        """
        # 별도 스레드에서 API 요청 실행
        thread = threading.Thread(target=self._send_log_data_thread, args=(log_data,))
        thread.daemon = True  # 메인 스레드 종료 시 함께 종료
        thread.start()
    
            
    def send_game_event(self, game_id, event_type, event_data):
        """
        게임 이벤트 전송
        
        Args:
            game_id (str): 게임 ID
            event_type (str): 이벤트 유형
            event_data (dict): 이벤트 데이터
            
        Returns:
            dict: API 응답 데이터
        """
        endpoint = f"{self.api_url}/games/{game_id}/events"
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps({
                    "type": event_type,
                    "data": event_data
                })
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.text else None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            }
    
    def send_game_state_update(self, game_id, game_state):
        """
        게임 상태 업데이트 전송
        
        Args:
            game_id (str): 게임 ID
            game_state (dict): 게임 상태 데이터
            
        Returns:
            dict: API 응답 데이터
        """
        endpoint = f"{self.api_url}/games/{game_id}/state"
        
        try:
            response = requests.put(
                endpoint,
                headers=self.headers,
                data=json.dumps(game_state)
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.text else None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            }
            
    def send_game_end(self, game_id, game_result):
        """
        게임 종료 이벤트 전송
        
        Args:
            game_id (str): 게임 ID
            game_result (dict): 게임 결과 데이터
            
        Returns:
            dict: API 응답 데이터
        """
        endpoint = f"{self.api_url}/games/{game_id}/end"
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps(game_result)
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "response": response.json() if response.text else None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            } 