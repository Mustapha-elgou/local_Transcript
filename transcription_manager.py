"""
FICHIER: transcription_manager.py
Description: Gère la sauvegarde et l'export des transcriptions
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from config import Config

class TranscriptionManager:
    """Gestionnaire de transcriptions avec sauvegarde et export"""
    
    def __init__(self):
        self.transcriptions = []
        self.current_session_file = None
        self.start_new_session()
    
    def start_new_session(self):
        """Démarre une nouvelle session de transcription"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session_file = f"session_{timestamp}"
        self.transcriptions = []
        print(f"✓ Nouvelle session créée: {self.current_session_file}")
    
    def add_transcription(self, text, timestamp=None):
        """Ajoute une transcription"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        entry = {
            'timestamp': timestamp,
            'text': text,
            'session': self.current_session_file
        }
        
        self.transcriptions.append(entry)
        
        # Sauvegarde automatique si activée
        if Config.SAVE_TRANSCRIPTIONS:
            self.auto_save()
        
        return entry
    
    def auto_save(self):
        """Sauvegarde automatique en JSON"""
        try:
            filepath = Path(Config.TRANSCRIPTION_FOLDER) / f"{self.current_session_file}.json"
            
            data = {
                'session': self.current_session_file,
                'created_at': datetime.now().isoformat(),
                'total_transcriptions': len(self.transcriptions),
                'transcriptions': self.transcriptions
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"Erreur de sauvegarde automatique: {e}")
    
    def export_to_txt(self, filename=None):
        """Exporte les transcriptions en TXT"""
        if filename is None:
            filename = f"{self.current_session_file}.txt"
        
        filepath = Path(Config.TRANSCRIPTION_FOLDER) / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"=== Session de Transcription ===\n")
                f.write(f"Session: {self.current_session_file}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total: {len(self.transcriptions)} transcriptions\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in self.transcriptions:
                    f.write(f"[{entry['timestamp']}]\n")
                    f.write(f"{entry['text']}\n\n")
            
            print(f"✓ Export TXT réussi: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Erreur d'export TXT: {e}")
            return None
    
    def export_to_json(self, filename=None):
        """Exporte les transcriptions en JSON"""
        if filename is None:
            filename = f"{self.current_session_file}_export.json"
        
        filepath = Path(Config.TRANSCRIPTION_FOLDER) / filename
        
        try:
            data = {
                'session': self.current_session_file,
                'exported_at': datetime.now().isoformat(),
                'total_transcriptions': len(self.transcriptions),
                'transcriptions': self.transcriptions
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Export JSON réussi: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Erreur d'export JSON: {e}")
            return None
    
    def export_to_csv(self, filename=None):
        """Exporte les transcriptions en CSV"""
        if filename is None:
            filename = f"{self.current_session_file}.csv"
        
        filepath = Path(Config.TRANSCRIPTION_FOLDER) / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Texte', 'Session'])
                
                for entry in self.transcriptions:
                    writer.writerow([
                        entry['timestamp'],
                        entry['text'],
                        entry['session']
                    ])
            
            print(f"✓ Export CSV réussi: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Erreur d'export CSV: {e}")
            return None
    
    def get_all_transcriptions(self):
        """Retourne toutes les transcriptions de la session"""
        return self.transcriptions
    
    def get_transcription_count(self):
        """Retourne le nombre total de transcriptions"""
        return len(self.transcriptions)
    
    def clear_transcriptions(self):
        """Efface toutes les transcriptions de la session actuelle"""
        self.transcriptions = []
        print("✓ Transcriptions effacées")
    
    def search_transcriptions(self, keyword):
        """Recherche dans les transcriptions"""
        results = []
        for entry in self.transcriptions:
            if keyword.lower() in entry['text'].lower():
                results.append(entry)
        return results
    
    def get_statistics(self):
        """Retourne des statistiques sur la session"""
        if not self.transcriptions:
            return {
                'total': 0,
                'first_timestamp': None,
                'last_timestamp': None,
                'average_length': 0
            }
        
        total_length = sum(len(t['text']) for t in self.transcriptions)
        
        return {
            'total': len(self.transcriptions),
            'first_timestamp': self.transcriptions[0]['timestamp'],
            'last_timestamp': self.transcriptions[-1]['timestamp'],
            'average_length': total_length // len(self.transcriptions),
            'total_characters': total_length
        }