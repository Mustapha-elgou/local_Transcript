"""
FICHIER: config.py
Description: Configuration de l'application
"""

import os

class Config:
    """Configuration générale de l'application"""
    
    # Configuration Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre_cle_secrete_super_securisee_2024'
    DEBUG = True
    
    # Configuration Socket.IO
    CORS_ALLOWED_ORIGINS = "*"
    
    # Configuration Audio
    AUDIO_FORMAT = 'paInt16'
    AUDIO_CHANNELS = 2
    AUDIO_RATE = 44100
    AUDIO_CHUNK_SIZE = 1024
    AUDIO_BUFFER_SECONDS = 3  # Durée du buffer avant transcription
    
    # Configuration Transcription
    LANGUAGE = 'fr-FR'  # Langue par défaut (français)
    # Autres langues disponibles:
    # 'en-US' : Anglais américain
    # 'en-GB' : Anglais britannique
    # 'ar-DZ' : Arabe algérien
    # 'es-ES' : Espagnol
    # 'de-DE' : Allemand
    # 'it-IT' : Italien
    
    # Configuration Sauvegarde
    SAVE_TRANSCRIPTIONS = True
    TRANSCRIPTION_FOLDER = 'transcriptions'
    AUTO_SAVE_INTERVAL = 30  # Sauvegarde automatique toutes les 30 secondes
    
    # Configuration Export
    EXPORT_FORMATS = ['txt', 'json', 'csv']
    
    # Mots-clés pour détecter le périphérique loopback
    LOOPBACK_KEYWORDS = [
        'stereo mix',
        'mixage',
        'what u hear',
        'wave out',
        'loopback',
        'monitor'
    ]
    
    @staticmethod
    def init_app():
        """Initialise l'application (crée les dossiers nécessaires)"""
        if Config.SAVE_TRANSCRIPTIONS:
            os.makedirs(Config.TRANSCRIPTION_FOLDER, exist_ok=True)
            print(f"✓ Dossier de transcription créé: {Config.TRANSCRIPTION_FOLDER}")