import os
import configparser
from dotenv import load_dotenv

# 설정 파일 경로
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.ini')

# 기본 설정값
DEFAULT_CONFIG = {
    'API': {
        'API_URL': 'https://example.com/api/hearthstone',
        'API_KEY': ''
    },
    'Paths': {
        'HEARTHSTONE_PATH': '',
        'LOG_PATH': ''
    },
    'Settings': {
        'MONITOR_INTERVAL': '5'
    }
}

# 설정 로드
def load_config():
    config = configparser.ConfigParser()
    
    # 기본 설정 적용
    for section, options in DEFAULT_CONFIG.items():
        if not config.has_section(section):
            config.add_section(section)
        for option, value in options.items():
            config.set(section, option, value)
    
    # 설정 파일이 있으면 로드
    if os.path.exists(CONFIG_FILE):
        try:
            config.read(CONFIG_FILE, encoding='utf-8')
            print(f"설정 파일을 로드했습니다: {CONFIG_FILE}")
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}")
            # 오류 발생 시 새 설정 파일 생성
            save_config(config)
    
    # 그래도 없는 값이 있으면 .env 파일에서 로드
    load_dotenv()
    
    # .env 파일의 값으로 덮어쓰기
    if os.getenv('API_URL'):
        config.set('API', 'API_URL', os.getenv('API_URL'))
    if os.getenv('API_KEY'):
        config.set('API', 'API_KEY', os.getenv('API_KEY'))
    if os.getenv('HEARTHSTONE_PATH'):
        config.set('Paths', 'HEARTHSTONE_PATH', os.getenv('HEARTHSTONE_PATH'))
    
    return config

# 설정 저장
def save_config(config):
    try:
        # 디렉토리가 없으면 생성
        config_dir = os.path.dirname(CONFIG_FILE)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        # 설정 파일 저장
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        
        print(f"설정 파일을 저장했습니다: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"설정 파일 저장 오류: {e}")
        return False

# 설정 인스턴스 생성
CONFIG = load_config()

# API 설정
API_URL = CONFIG.get('API', 'API_URL')
API_KEY = CONFIG.get('API', 'API_KEY')

# 경로 설정
HEARTHSTONE_PATH = CONFIG.get('Paths', 'HEARTHSTONE_PATH')
LOG_PATH = CONFIG.get('Paths', 'LOG_PATH')

# 로그 경로가 설정되지 않았으면 하스스톤 경로에서 추론
if not LOG_PATH and HEARTHSTONE_PATH:
    LOG_PATH = os.path.join(HEARTHSTONE_PATH, 'Logs')
# 둘 다 없으면 기본 경로 사용
elif not LOG_PATH:
    LOG_PATH = os.path.expanduser("~\\AppData\\Local\\Blizzard\\Hearthstone\\Logs")

# 모니터링 간격 설정
MONITOR_INTERVAL = int(CONFIG.get('Settings', 'MONITOR_INTERVAL'))

# 사용할 로그 파일 목록
LOG_FILES = [
    "Power.log",
    "LoadingScreen.log",
    "Asset.log",
    "Arena.log",
    "Achievements.log"
]

# 기본 하스스톤 로그 경로 
DEFAULT_LOG_PATH = LOG_PATH 