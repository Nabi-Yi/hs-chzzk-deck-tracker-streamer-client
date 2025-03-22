import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import configparser
import os
import re
from datetime import datetime

# 로그 파서 모듈 임포트
from log_parser import HSLogWatcher
from dotenv import load_dotenv
load_dotenv()

class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("하스스톤 - 치지직 덱 트래커")
        self.root.geometry("500x700")  # 높이 증가
        
        self.config_file = "settings.ini"
        self.config = configparser.ConfigParser()
        
        # 로그 감시 객체
        self.log_watcher = None
        
        # 변수 초기화
        self.install_path_var = tk.StringVar()
        self.log_path_preview_var = tk.StringVar()
        self.power_log_var = tk.StringVar()
        self.status_var = tk.StringVar(value="준비")
        self.is_running = tk.BooleanVar(value=False)
        self.api_key_var = tk.StringVar()  # API 키 변수 추가
        
        # 메시지 큐 (log_text가 초기화되기 전 메시지 저장용)
        self.message_queue = []
        
        # 로그 텍스트 위젯 (반드시 여기서 초기화)
        self.log_text = None
        self.field_log_text = None
        
        # 위젯 생성
        self.create_widgets()
        
        # 큐에 있는 메시지 처리
        self.process_message_queue()
        

        if not self.log_watcher:
            self.log_watcher = HSLogWatcher(self.add_log, self.is_running)
            self.log_watcher.set_root(self.root)
        # 설정 로드 (위젯 생성 후에 로드하여 로그 출력 가능)
        self.load_config()


    
    def process_message_queue(self):
        """큐에 저장된 메시지 처리"""
        if self.log_text and self.message_queue:
            for message in self.message_queue:
                self.add_log(message)
            self.message_queue = []
    
    def load_config(self):
        """설정 파일 로드"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self.add_log("설정 파일을 로드했습니다.")
            
            # 설치 경로가 있으면 UI 업데이트, log_watcher에 설치 경로 전달
            if 'Paths' in self.config and 'install_path' in self.config['Paths']:
                self.install_path_var.set(self.config['Paths']['install_path'])
                self.log_watcher.set_install_path(self.config['Paths']['install_path'])
            
            # API 키 로드
            if 'API' in self.config and 'api_key' in self.config['API']:
                self.api_key_var.set(self.config['API']['api_key'])
                if hasattr(self.log_watcher, 'api_sender') and self.log_watcher.api_sender:
                    self.log_watcher.api_sender.set_api_key(self.config['API']['api_key'])

        else:
            self.add_log("settings.ini 파일을 찾을 수 없습니다. 새 설정 파일을 생성합니다.")
            self.config['Paths'] = {}
            self.config['API'] = {}
    
    def save_config(self):
        """설정 파일 저장"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
        self.add_log("설정이 저장되었습니다.")

    
    def browse_install_path(self):
        """설치 경로 탐색"""
        folder_path = filedialog.askdirectory(title="하스스톤 설치 폴더 선택")
        if folder_path:
            self.install_path_var.set(folder_path)
            self.log_watcher.set_install_path(folder_path)
            # 로그 경로 미리보기 업데이트
    
    def toggle_monitoring(self):
        """로그 감시 시작/중지"""
        if self.is_running.get():
            # 중지
            self.is_running.set(False)
            self.add_log("로그 감시가 중지되었습니다.")
            self.start_btn.config(text="시작")
            self.log_watcher.stop_log_watcher()
        else:
            # 시작
            self.log_watcher.start_log_watcher()
            self.is_running.set(True)
            self.start_btn.config(text="중지")
            self.add_log("하스스톤 로그 감시를 시작합니다.")
            
    
    def add_log(self, message: str):
        """로그창에 메시지 추가"""
        try:
            if self.log_text:
                # 필드 로그인 경우
                if message.startswith("필드:"):
                    self.update_field_log(message)
                    return
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.log_text.configure(state="normal")
                self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state="disabled")
            else:
                # 로그 텍스트가 초기화되지 않은 경우 큐에 메시지 저장
                self.message_queue.append(message)
                print(f"로그 메시지 큐에 추가: {message}")
        except Exception as e:
            print(f"로그 추가 오류: {str(e)}")
    
    def update_field_log(self, message: str):
        """필드 로그창 업데이트 (항상 최신 정보만 표시)"""
        try:
            if self.field_log_text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.field_log_text.configure(state="normal")
                self.field_log_text.delete(1.0, tk.END)  # 기존 내용 모두 삭제
                self.field_log_text.insert(tk.END, f"[{timestamp}] {message}\n")
                self.field_log_text.see(tk.END)
                self.field_log_text.configure(state="disabled")
        except Exception as e:
            print(f"필드 로그 업데이트 오류: {str(e)}")
    
    def create_widgets(self):
        """GUI 위젯 생성"""
        # 제목
        tk.Label(self.root, text="하스스톤 - 치지직 덱트래커", font=("Arial", 16)).pack(pady=10)
        
        # 설정 프레임
        frame = tk.Frame(self.root)
        frame.pack(pady=5, fill="x", padx=20)
        
        # 설치 경로 설정
        tk.Label(frame, text="설치 경로:", width=12, anchor="w").grid(row=0, column=0, pady=5, sticky="w")
        
        install_entry = tk.Entry(frame, textvariable=self.install_path_var, width=40)
        install_entry.grid(row=0, column=1, pady=5, padx=5)
        
        browse_btn = tk.Button(frame, text="찾아보기", command=self.browse_install_path)
        browse_btn.grid(row=0, column=2, pady=5)
        
        # 로그 경로 미리보기
        # tk.Label(frame, text="로그 경로:", width=12, anchor="w").grid(row=1, column=0, pady=5, sticky="w")
        
        # log_path_preview = tk.Entry(frame, textvariable=self.log_path_preview_var, width=40, state="readonly")
        # log_path_preview.grid(row=1, column=1, pady=5, padx=5)
        
        # Power.log 파일 경로
        # tk.Label(frame, text="Power.log:", width=12, anchor="w").grid(row=2, column=0, pady=5, sticky="w")
            
        # power_log_entry = tk.Entry(frame, textvariable=self.power_log_var, width=40, state="readonly")
        # power_log_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # API 키 입력 필드 추가
        tk.Label(frame, text="API 키:", width=12, anchor="w").grid(row=3, column=0, pady=5, sticky="w")
        
        api_key_entry = tk.Entry(frame, textvariable=self.api_key_var, width=40)
        api_key_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # 저장 버튼
        save_btn = tk.Button(frame, text="설정 저장", command=self.save_settings)
        save_btn.grid(row=3, column=2, pady=5)
        
        # 상태 표시 레이블
        status_label = tk.Label(self.root, textvariable=self.status_var)
        status_label.pack(pady=5)
        
        # 시작/중지 버튼
        self.start_btn = tk.Button(self.root, text="시작", width=10, command=self.toggle_monitoring)
        self.start_btn.pack(pady=5)
        
        # # 필드 로그창 제목
        # tk.Label(self.root, text="현재 필드 상태", anchor="w").pack(pady=(10,0), padx=20, anchor="w")
        
        # # 필드 로그창 (최신 정보만 표시)
        # self.field_log_text = scrolledtext.ScrolledText(self.root, height=20, width=60, state="disabled")
        # self.field_log_text.pack(pady=5, padx=20, fill="x")
        
        # 일반 로그창 제목
        tk.Label(self.root, text="로그", anchor="w").pack(pady=(10,0), padx=20, anchor="w")
        
        # 일반 로그창 (스크롤 가능한 텍스트 영역)
        self.log_text = scrolledtext.ScrolledText(self.root, height=5, width=60, state="disabled")
        self.log_text.pack(pady=5, padx=20, fill="both", expand=True)
        
        # 시작 로그 - 이제 log_text가 초기화된 후에 호출
        self.add_log("프로그램이 시작되었습니다.")
    
    def save_settings(self):
        """설정 저장"""
        if not 'Paths' in self.config:
            self.config['Paths'] = {}
        
        if not 'API' in self.config:
            self.config['API'] = {}
        
        install_path = self.install_path_var.get()
        api_key = self.api_key_var.get()
        
        self.config['Paths']['install_path'] = install_path
        self.config['API']['api_key'] = api_key
        
        # API 키를 로그 와처에 전달
        if hasattr(self.log_watcher, 'api_sender') and self.log_watcher.api_sender:
            self.log_watcher.api_sender.set_api_key(api_key)
        
        # 로그 경로는 설치 경로 + /Logs로 자동 설정
        if install_path:
            log_path = os.path.join(install_path, "Logs")
            self.config['Paths']['log_path'] = log_path
        
        self.save_config()
        
        # 상태 업데이트
        self.status_var.set("설정이 저장되었습니다.")
        self.root.after(3000, lambda: self.status_var.set("준비"))

def main():
    root = tk.Tk()
    app = SettingsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()