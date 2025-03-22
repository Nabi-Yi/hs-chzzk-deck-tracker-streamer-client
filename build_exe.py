import os
import subprocess
import sys

def build_exe():
    """PyInstaller를 사용하여 EXE 파일 생성"""
    print("하스스톤 로그 모니터링 EXE 파일 생성을 시작합니다...")
    
    # 설정 파일이 없으면 생성
    if not os.path.exists("settings.ini"):
        import config
        config.save_config(config.CONFIG)
        print("settings.ini 파일이 생성되었습니다.")
    
    # python-hslog 경로 추가
    hslog_path = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'python-hslog')
    if os.path.exists(hslog_path):
        sys.path.append(hslog_path)
        print(f"python-hslog 경로 추가: {hslog_path}")
    else:
        print(f"경고: python-hslog 디렉토리가 존재하지 않습니다: {hslog_path}")
    
    # 먼저 spec 파일 생성
    print("spec 파일 생성 중...")
    spec_cmd = [
        "pyi-makespec",
        "--name=hs-chzzk-streamer-client",
        "--onedir",
        "--noupx",
        "--specpath=.",
        "--hidden-import=site",
        "--hidden-import=hslog",
        "--hidden-import=hslog.parser",
        "--hidden-import=hslog.export",
        "--hidden-import=hearthstone", 
        "--hidden-import=hearthstone.enums",
        "--hidden-import=hearthstone.entities",
        f"--paths={hslog_path}",
        "--add-data=settings.ini;.",
        "--add-data=python-hslog;python-hslog",
        "--add-data=.env;." if os.path.exists(".env") else "--add-data=.env.example;.",
        "--runtime-tmpdir=.",
        "--icon=icon.ico" if os.path.exists("icon.ico") else "",
        "gui.py"
    ]
    
    # 명령에서 빈 문자열 항목 제거
    spec_cmd = [item for item in spec_cmd if item]
    
    try:
        # spec 파일 생성
        subprocess.run(spec_cmd, check=True)
        print("spec 파일이 생성되었습니다: hs-chzzk-streamer-client.spec")
        
        # 빌드 진행
        print("빌드 진행 중...")
        build_cmd = [
            "pyinstaller",
            "--clean",
            "--workpath=./build",
            "--distpath=./dist",
            "--noconfirm",
            "hs-chzzk-streamer-client.spec"
        ]
        
        subprocess.run(build_cmd, check=True)
        
        print("\n빌드 완료!")
        print("생성된 폴더 위치: dist/hs-chzzk-streamer-client")
        print("실행 파일 위치: dist/hs-chzzk-streamer-client/hs-chzzk-streamer-client.exe")
        
        # 생성된 EXE 파일 테스트 여부 확인
        test_exe = input("\n생성된 EXE 파일을 테스트하시겠습니까? (y/n): ")
        if test_exe.lower() == 'y':
            print("\n생성된 EXE 파일을 실행합니다...")
            subprocess.run(["dist/hs-chzzk-streamer-client/hs-chzzk-streamer-client.exe", "--console"])
        
    except subprocess.CalledProcessError as e:
        print(f"빌드 실패: {e}")
        return False
    except FileNotFoundError:
        print("오류: PyInstaller가 설치되어 있지 않습니다.")
        print("pip install pyinstaller를 실행하여 설치해주세요.")
        return False
    
    return True

if __name__ == "__main__":
    # 기본 설정 파일 생성을 위한 import
    import config
    
    # 기본 설정 파일이 없으면 생성
    if not os.path.exists("settings.ini"):
        config.save_config(config.CONFIG)
        print("settings.ini 파일이 생성되었습니다.")
    else:
        print("기존 settings.ini 파일을 사용합니다.")
    
    # 파일이 생성되었는지 확인
    if not os.path.exists("settings.ini"):
        print("오류: settings.ini 파일을 생성할 수 없습니다.")
        sys.exit(1)
    
    # EXE 빌드
    build_exe() 