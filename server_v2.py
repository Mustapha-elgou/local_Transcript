"""
FICHIER: server_v2.py
Description: Serveur Flask amélioré avec sauvegarde et export
"""

import threading
import queue
from datetime import datetime
from flask import Flask, render_template, jsonify, send_file
from flask_socketio import SocketIO, emit
import speech_recognition as sr
import pyaudio
from config import Config
from transcription_manager import TranscriptionManager

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ALLOWED_ORIGINS)

class AudioTranscriber:
    def __init__(self, transcription_manager):
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.device_index = None
        self.manager = transcription_manager
        
    def get_loopback_device(self):
        """Trouve le périphérique de loopback (Stereo Mix)"""
        p = pyaudio.PyAudio()
        loopback_index = None
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            device_name = info['name'].lower()
            
            if info['maxInputChannels'] > 0:
                for keyword in Config.LOOPBACK_KEYWORDS:
                    if keyword in device_name:
                        loopback_index = i
                        print(f"✓ Périphérique loopback trouvé: {info['name']}")
                        break
            
            if loopback_index is not None:
                break
        
        p.terminate()
        return loopback_index
    
    def record_system_audio(self):
        """Enregistre l'audio système"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=Config.AUDIO_CHANNELS,
                rate=Config.AUDIO_RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=Config.AUDIO_CHUNK_SIZE
            )
            
            print("🎙️ Enregistrement de l'audio système en cours...")
            socketio.emit('status', {'status': 'recording', 'message': 'Enregistrement en cours...'})
            
            while self.is_recording:
                try:
                    data = stream.read(Config.AUDIO_CHUNK_SIZE, exception_on_overflow=False)
                    self.audio_queue.put(data)
                except Exception as e:
                    print(f"Erreur lecture audio: {e}")
                    
        except Exception as e:
            print(f"Erreur d'enregistrement: {e}")
            socketio.emit('error', {'message': str(e)})
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
    
    def process_audio_chunks(self):
        """Traite et transcrit les chunks audio"""
        audio_buffer = []
        chunks_per_transcription = int(Config.AUDIO_RATE * Config.AUDIO_BUFFER_SECONDS / Config.AUDIO_CHUNK_SIZE)
        
        while self.is_recording or not self.audio_queue.empty():
            try:
                chunk = self.audio_queue.get(timeout=1)
                audio_buffer.append(chunk)
                
                if len(audio_buffer) >= chunks_per_transcription:
                    self.transcribe_buffer(audio_buffer)
                    audio_buffer = []
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Erreur traitement: {e}")
    
    def transcribe_buffer(self, audio_buffer):
        """Transcrit un buffer audio"""
        try:
            audio_data = b''.join(audio_buffer)
            audio = sr.AudioData(audio_data, Config.AUDIO_RATE, 2)
            
            # Transcription
            text = self.recognizer.recognize_google(audio, language=Config.LANGUAGE)
            
            if text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Sauvegarde dans le gestionnaire
                entry = self.manager.add_transcription(text, timestamp)
                
                # Envoie au client web
                socketio.emit('transcription', entry)
                
                # Envoie les statistiques
                stats = self.manager.get_statistics()
                socketio.emit('statistics', stats)
                
                print(f"[{timestamp}] {text}")
                
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Erreur API: {e}")
            socketio.emit('error', {'message': f'Erreur API: {e}'})
        except Exception as e:
            print(f"Erreur transcription: {e}")
    
    def start_recording(self):
        """Démarre l'enregistrement"""
        if self.is_recording:
            return False
        
        self.device_index = self.get_loopback_device()
        
        if self.device_index is None:
            error_msg = "Aucun périphérique loopback trouvé. Activez 'Stereo Mix' dans les paramètres Windows."
            socketio.emit('error', {'message': error_msg})
            return False
        
        self.is_recording = True
        
        # Nouvelle session
        self.manager.start_new_session()
        
        # Lance les threads
        record_thread = threading.Thread(target=self.record_system_audio)
        process_thread = threading.Thread(target=self.process_audio_chunks)
        
        record_thread.daemon = True
        process_thread.daemon = True
        
        record_thread.start()
        process_thread.start()
        
        return True
    
    def stop_recording(self):
        """Arrête l'enregistrement"""
        self.is_recording = False
        socketio.emit('status', {'status': 'stopped', 'message': 'Arrêté'})
        print("⏹️ Enregistrement arrêté")

# Instances globales
Config.init_app()
manager = TranscriptionManager()
transcriber = AudioTranscriber(manager)

@app.route('/')
def index():
    """Page principale"""
    return render_template('index_v2.html')

@app.route('/api/export/<format>')
def export_transcriptions(format):
    """Exporte les transcriptions dans le format demandé"""
    try:
        if format == 'txt':
            filepath = manager.export_to_txt()
        elif format == 'json':
            filepath = manager.export_to_json()
        elif format == 'csv':
            filepath = manager.export_to_csv()
        else:
            return jsonify({'error': 'Format non supporté'}), 400
        
        if filepath:
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Erreur d\'export'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """Retourne les statistiques de la session"""
    stats = manager.get_statistics()
    return jsonify(stats)

@app.route('/api/search/<keyword>')
def search_transcriptions(keyword):
    """Recherche dans les transcriptions"""
    results = manager.search_transcriptions(keyword)
    return jsonify(results)

@socketio.on('connect')
def handle_connect():
    """Gère la connexion d'un client"""
    print('Client connecté')
    emit('status', {'status': 'connected', 'message': 'Connecté au serveur'})
    
    # Envoie les transcriptions existantes
    transcriptions = manager.get_all_transcriptions()
    emit('load_transcriptions', {'transcriptions': transcriptions})

@socketio.on('disconnect')
def handle_disconnect():
    """Gère la déconnexion d'un client"""
    print('Client déconnecté')
    transcriber.stop_recording()

@socketio.on('start_recording')
def handle_start_recording():
    """Démarre l'enregistrement"""
    success = transcriber.start_recording()
    if success:
        emit('status', {'status': 'recording', 'message': 'Enregistrement démarré'})
    else:
        emit('status', {'status': 'error', 'message': 'Erreur de démarrage'})

@socketio.on('stop_recording')
def handle_stop_recording():
    """Arrête l'enregistrement"""
    transcriber.stop_recording()
    emit('status', {'status': 'stopped', 'message': 'Arrêté'})

@socketio.on('clear_transcriptions')
def handle_clear():
    """Efface les transcriptions"""
    manager.clear_transcriptions()
    emit('transcriptions_cleared', broadcast=True)

@socketio.on('request_statistics')
def handle_statistics_request():
    """Envoie les statistiques"""
    stats = manager.get_statistics()
    emit('statistics', stats)

if __name__ == '__main__':
    print("=" * 60)
    print("🎯 SERVEUR DE TRANSCRIPTION AUDIO SYSTÈME V2")
    print("=" * 60)
    print("\n✨ Nouvelles fonctionnalités:")
    print("  • Sauvegarde automatique")
    print("  • Export TXT, JSON, CSV")
    print("  • Statistiques en temps réel")
    print("  • Recherche dans les transcriptions")
    print("\n📌 INSTRUCTIONS:")
    print("1. Activez 'Stereo Mix' dans Windows")
    print("2. Ouvrez: http://localhost:5000")
    print("3. Lancez de l'audio dans Chrome/Edge")
    print("4. Cliquez sur 'Démarrer'")
    print(f"\n💾 Transcriptions sauvegardées dans: {Config.TRANSCRIPTION_FOLDER}/")
    print("\n🌐 Serveur démarré sur http://localhost:5000")
    print("=" * 60 + "\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)