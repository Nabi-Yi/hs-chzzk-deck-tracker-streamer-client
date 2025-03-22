import sys
import os
import re
from datetime import datetime
import traceback
import gc

# python-hslog 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'python-hslog'))
from hslog.parser import LogParser
from hslog.export import EntityTreeExporter, FriendlyPlayerExporter 
from hearthstone.enums import GameTag, Zone
from hearthstone.entities import Card, Game, Player
from typing import assert_type
from api_sender import LogApiSender


class HSLogWatcher:
    def __init__(self, callback_func=None, is_running=None):
        self.log_path = None
        self.parser = LogParser()  # 다시 초기화
        self.callback = callback_func
        self.is_mounted = False
        self.last_log_path = None
        self.install_path = None
        self.is_running = is_running
        self.root = None
        self.after_id = None
        self.exporter =None
        self.api_sender = LogApiSender()
        

    def set_install_path(self, path):
        self.install_path = path

    def set_log_path(self, path):
        if path != self.log_path:
            self.log_path = path
            self.last_log_path = path
            if self.callback:
                self.callback(f"로그 파일 설정: {path}")
            # 새 로그 경로로 변경되면 파서 재설정
            self.parser = LogParser()
    
    def mount_log_file(self):
        """로그 파일 마운트"""
        new_log_path = self.find_latest_log_file(self.install_path)
        if not os.path.exists(new_log_path):
            print("로그 파일을 찾을 수 없습니다.")
            return False
        
        # 아예 없었던 경우
        if not self.log_path or not os.path.exists(self.log_path):
            if new_log_path:
                self.set_log_path(new_log_path)
                self.callback(f"새로운 로그 파일 경로: {new_log_path}")
            else:
                self.callback("로그 파일을 찾을 수 없습니다.")
                return False

        # 이전 경로와 다르면 로그 추가
        if new_log_path != self.last_log_path:
            if self.callback:
                self.callback(f"최신 Power.log 파일을 발견했습니다: {new_log_path}")
            self.set_log_path(new_log_path)
        else:
            return True

    def parse_log_file(self):
        try:
            # 가비지 컬렉션 명시적 호출
            gc.collect()
            self.parser = LogParser()  # LogParser 내부 로직으로 인해 매번 새로 생성
            # 로그 파일 열기 시도 (읽기 권한 확인)
            with open(self.log_path, 'r', encoding='utf-8') as f:
                self.parser.read(f)
                self.is_mounted = True
                # print(f"게임 로그 파싱 완료: {len(self.parser.games)} 게임(들)")
                return True
        except Exception as e:
            print(e)
            self.is_mounted = False
            if self.callback:
                self.callback(f"게임 시작 대기중...")
            return False

    
    def find_latest_log_file(self, install_path):
        """최신 로그 폴더와 Power.log 파일 찾기"""
        logs_dir = os.path.join(install_path, "Logs")
        if not os.path.exists(logs_dir):
            if self.callback:
                self.callback(f"로그 폴더가 존재하지 않습니다: {install_path}")
            return None
        
        # 하스스톤 로그 폴더 패턴 (Hearthstone_YYYY_MM_DD_HH_MM_SS)
        pattern = re.compile(r'Hearthstone_\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}')
        
        # 폴더 찾기
        log_folders = []
        for folder in os.listdir(logs_dir):
            folder_path = os.path.join(logs_dir, folder)
            if os.path.isdir(folder_path) and pattern.match(folder):
                # 날짜 추출
                date_parts = folder.replace('Hearthstone_', '').split('_')
                if len(date_parts) == 6:
                    try:
                        folder_date = datetime(
                            int(date_parts[0]), int(date_parts[1]), int(date_parts[2]),
                            int(date_parts[3]), int(date_parts[4]), int(date_parts[5])
                        )
                        log_folders.append((folder_path, folder_date))
                    except ValueError:
                        continue
        
        if not log_folders:
            if self.callback:
                self.callback("로그 폴더를 찾을 수 없습니다.")
            return None
        
        # 최신 폴더 정렬
        log_folders.sort(key=lambda x: x[1], reverse=True)
        latest_folder = log_folders[0][0]
        
        # Power.log 파일 찾기
        power_log_path = os.path.join(latest_folder, "Power.log")
        return power_log_path
    
    def get_my_hand(self,me,game):
        try:
            minions = []
            for entity in game.entities:
                if assert_type(entity, Card):
                    if entity.zone == Zone.HAND and entity.tags[GameTag.CONTROLLER] == me.tags[GameTag.CONTROLLER] :
                        minions.append({"id": entity.id,
                                        "realId":entity.tags.get(GameTag.CREATOR_DBID,0),
                                        "cardId": entity.card_id if hasattr(entity, 'card_id') and entity.card_id else None})
            return minions
        except Exception as e:
            print(e)
            traceback.print_exc()
            if self.callback:
                self.callback(f"핸드 가져오기 오류 발생: {str(e)}")
            return []
        
    def get_field(self,player,game):
        try:
            minions = []
            for entity in game.entities:
                if assert_type(entity, Card):
                    if entity.zone == Zone.PLAY and entity.tags[GameTag.CONTROLLER] == player.tags[GameTag.CONTROLLER]:
                        minions.append({"id": entity.id,
                                        "realId":entity.tags.get(GameTag.CREATOR_DBID,0),
                                        "cardId": entity.card_id if hasattr(entity, 'card_id') and entity.card_id else None})
            return minions
        except Exception as e:
            print(e)
            traceback.print_exc()
            if self.callback:
                self.callback(f"필드 가져오기 오류 발생: {str(e)}")
            return []
        
    def get_grave(self,player):
        try:
            graves = []
            for entity in player.entities:
                if assert_type(entity, Card):   
                    if entity.zone == Zone.GRAVEYARD:
                        graves.append({"id": entity.id,
                                        "realId":entity.tags.get(GameTag.CREATOR_DBID,0),
                                        "cardId": entity.card_id if hasattr(entity, 'card_id') and entity.card_id else None})
            return graves
        except Exception as e:
            print(e)
            traceback.print_exc()
            if self.callback:
                self.callback(f"무덤 가져오기 오류 발생: {str(e)}")
            return []
    
    def get_all_player_cards(self,player):
        try:
            cards = []
            for entity in player.entities:
                try:
                    if assert_type(entity, Card):
                        cards.append({"id": entity.id,
                                    "realId":entity.tags.get(GameTag.CREATOR_DBID,0),
                                    "cardId": entity.card_id if hasattr(entity, 'card_id') and entity.card_id else None})
                except Exception as e:
                    print(e)
            return cards
        except Exception as e:
            print(e)
            traceback.print_exc()

            if self.callback:
                self.callback(f"모든 플레이어 카드 가져오기 오류 발생: {str(e)}")
            return []
        
    def get_last_game_players(self):
        try:
            games = self.parser.games
            last_game = games[-1]
            # 플레이어 정보 가져오기
            fExporter = FriendlyPlayerExporter(last_game)
            myId = fExporter.export()
            # 게임 정보 가져오기
            self.exporter = EntityTreeExporter(last_game)
            exported_game = self.exporter.export().game
            if not exported_game:
                return None
            # 플레이어 정보 매칭
            players = exported_game.players
            me = None
            enemy = None
            for player in players:
                if player.player_id == myId:
                    me = player
                else:
                    enemy = player
            return me, enemy, exported_game

        except Exception as e:
            print(e)
            traceback.print_exc()
            # if self.callback:
            #     self.callback(f"마지막 게임 가져오기 오류 발생: {str(e)}")
            return None

    def get_all_cards(self,game):
        try:
            cards = []
            for entity in game.entities:
                if assert_type(entity, Card):
                    cards.append({"id": entity.id,
                                 "realId":entity.tags.get(GameTag.CREATOR_DBID,0),
                                 "cardId": entity.card_id if hasattr(entity, 'card_id') and entity.card_id else None})
            return cards
        except Exception as e:
            print(e)
            traceback.print_exc()
            return []
    

    def schedular(self):
        try: 
        # 일정 주기마다 가비지 컬렉션 실행
            gc.collect()
            
            self.mount_log_file()
            self.parse_log_file()  # 다시 LogParser 생성

            if self.callback and self.is_mounted:
                me, enemy, last_game = self.get_last_game_players()

                # hand_data = self.get_my_hand(me,last_game)
                # my_field_data = self.get_field(me,last_game)
                # enemy_field_data = self.get_field(enemy,last_game)
                # my_grave_data = self.get_grave(me)
                # enemy_grave_data = self.get_grave(enemy)

                my_cards = self.get_all_player_cards(me)
                enemy_cards = self.get_all_player_cards(enemy)

                all_cards = self.get_all_cards(last_game)

                # 게임 데이터 수집
                game_data = {
                    "my_cards": my_cards,
                    "enemy_cards": enemy_cards,
                }
                
                # API로 데이터 전송 (비동기적으로 처리됨)
                self.api_sender.send_log_data(game_data)
                
                # UI에 필드 정보 표시
                # self.callback(f"내 카드: {len(my_cards)} {my_cards}\n\n적 카드: {len(enemy_cards)} {enemy_cards}\n")
        except Exception as e:
            # print(e)
            # traceback.print_exc()
            if self.callback:
                self.callback(f"일시적 오류 발생... 재시도중:")

        self.after_id = self.root.after(5000, self.schedular)

            

    def start_log_watcher(self):
        self.schedular()


    def stop_log_watcher(self):
        if self.callback:
            self.callback("로그 감시가 중지되었습니다.")
        # 파서 참조 해제
        self.parser = None  # 메모리 해제를 위해 None으로 설정
        self.is_mounted = False
        self.set_log_path(None)
        
        # 가비지 컬렉션 강제 실행
        gc.collect()
        
        # after_cancel을 사용하여 스케줄러 중지
        if self.root and self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def set_root(self, root):
        """루트 윈도우 설정"""
        self.root = root