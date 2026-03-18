import os
import wave
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QPushButton, QComboBox, QTextEdit, QFrame, QFileDialog, QScrollArea
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment

from utils.steganography import string_to_binary, binary_to_string
from utils.check_bit import get_audio_capacity_lsb
from utils.logger import logger

class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio = None
        self.capacity = 0
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # --- Top Section: Intro ---
        intro_layout = QVBoxLayout()
        title = QLabel("Hide Message in Audio")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: white;")
        subtitle = QLabel("Securely embed your secret messages into audio files using advanced LSB steganography.")
        subtitle.setObjectName("subTitle")
        intro_layout.addWidget(title)
        intro_layout.addWidget(subtitle)
        main_layout.addLayout(intro_layout)

        # --- Middle Section: Main Grid ---
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)

        # Left Column: Audio Selection & Playback
        left_col = QVBoxLayout()
        audio_group = QGroupBox("SELECT CARRIER AUDIO")
        audio_layout = QVBoxLayout(audio_group)
        
        self.path_label = QLabel("Drag and drop audio file\nMP3, WAV, or FLAC")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setMinimumSize(300, 100)
        self.path_label.setStyleSheet("""
            border: 2px dashed #1e293b;
            border-radius: 15px;
            color: #64748b;
            font-size: 11pt;
            background-color: #0b0e14;
        """)
        audio_layout.addWidget(self.path_label)
        
        # Audio Selection Buttons
        file_selection = QHBoxLayout()
        self.browse_btn = QPushButton("📁 Browse Files")
        self.browse_btn.clicked.connect(self.browse_audio)
        self.example_selector = QComboBox()
        self.example_selector.setPlaceholderText("Select Example...")
        self.example_selector.currentIndexChanged.connect(self.load_example_audio)
        file_selection.addWidget(self.browse_btn)
        file_selection.addWidget(self.example_selector)
        audio_layout.addLayout(file_selection)

        # Playback Controls
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_audio)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_btn)
        audio_layout.addLayout(playback_layout)
        
        left_col.addWidget(audio_group)
        grid_layout.addLayout(left_col, 3)

        # Right Column: Payload & Settings
        right_col = QVBoxLayout()
        
        # Payload Section
        payload_group = QGroupBox("SECRET MESSAGE")
        payload_layout = QVBoxLayout(payload_group)
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type the message you want to hide here...")
        self.message_input.textChanged.connect(self.update_capacity)
        payload_layout.addWidget(self.message_input)
        
        self.capacity_info = QLabel("Capacity: N/A | Used: 0 bits")
        self.capacity_info.setStyleSheet("color: #94a3b8; font-size: 9pt; margin-top: 5px;")
        payload_layout.addWidget(self.capacity_info)
        right_col.addWidget(payload_group)

        # Settings Section
        settings_group = QGroupBox("ENCODING PARAMETERS")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.addWidget(QLabel("Encoding Depth:"))
        self.depth_selector = QComboBox()
        self.depth_selector.addItems(["Low (Highest Quality)", "Medium (Balanced)", "High (Max Capacity)"])
        settings_layout.addWidget(self.depth_selector)
        right_col.addWidget(settings_group)
        
        grid_layout.addLayout(right_col, 2)
        main_layout.addLayout(grid_layout)

        # --- Bottom Section: Actions ---
        action_group = QGroupBox("ACTIONS")
        action_layout = QHBoxLayout(action_group)
        
        self.hide_btn = QPushButton("🔒 Hide Message")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 Extract Message")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        self.folder_btn = QPushButton("📁 Output Folder")
        self.folder_btn.clicked.connect(self.open_output_folder)
        
        action_layout.addWidget(self.hide_btn)
        action_layout.addWidget(self.extract_btn)
        action_layout.addWidget(self.folder_btn)
        main_layout.addWidget(action_group)
        
        # Logs
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Operation logs...")
        self.log_output.setMaximumHeight(100)
        main_layout.addWidget(self.log_output)
        
        self.load_examples()

    def load_examples(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        example_dir = os.path.join(base_dir, "audioexample")
        if os.path.exists(example_dir):
            files = [f for f in os.listdir(example_dir) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
            self.example_selector.addItems(files)

    def load_audio(self, path):
        logger.log("info", f"AudioTab: โหลดไฟล์เสียงจาก {path}")
        self.selected_audio = path
        self.path_label.setText(f"ไฟล์ที่เลือก: {os.path.basename(path)}")
        self.update_capacity()

    def browse_audio(self):
        path, _ = QFileDialog.getOpenFileName(self, "เลือกไฟล์เสียง", "", "Audio Files (*.wav *.mp3 *.flac)")
        if path: self.load_audio(path)

    def load_example_audio(self):
        name = self.example_selector.currentText()
        if name:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(base_dir, "audioexample", name)
            self.load_audio(path)

    def update_capacity(self):
        if not self.selected_audio: return
        self.capacity = get_audio_capacity_lsb(self.selected_audio)
        msg_len = len(self.message_input.toPlainText().encode('utf-8')) * 8
        self.capacity_info.setText(f"ความจุ: {self.capacity:,} บิต\nใช้ไป: {msg_len:,} บิต")
        if msg_len > self.capacity:
            self.capacity_info.setStyleSheet("color: #ff4444; background-color: #1a222d; border-radius: 10px; padding: 10px;")
        else:
            self.capacity_info.setStyleSheet("color: #00ff88; background-color: #1a222d; border-radius: 10px; padding: 10px;")

    def play_audio(self):
        if not self.selected_audio: return
        try:
            data, fs = sf.read(self.selected_audio)
            sd.play(data, fs)
        except Exception as e:
            self.log_output.append(f"❌ เล่นเสียงไม่ได้: {str(e)}")

    def stop_audio(self):
        sd.stop()

    def process_hide(self):
        if not self.selected_audio: return
        msg = self.message_input.toPlainText()
        if not msg: return
        logger.log("info", "AudioTab: เริ่มกระบวนการซ่อนข้อความในไฟล์เสียง")
        
        try:
            # แปลงเป็น WAV ชั่วคราวถ้าไม่ใช่ WAV
            use_path = self.selected_audio
            temp_wav = None
            if not self.selected_audio.lower().endswith('.wav'):
                audio = AudioSegment.from_file(self.selected_audio)
                temp_wav = "temp_audio.wav"
                audio.export(temp_wav, format="wav")
                use_path = temp_wav
            
            with wave.open(use_path, 'rb') as f:
                params = f.getparams()
                n_frames = f.getnframes()
                frames = f.readframes(n_frames)
            
            # ตรวจสอบขนาดตัวอย่าง (Sample Width)
            sample_width = params.sampwidth
            if sample_width == 1:
                audio_data = np.frombuffer(frames, dtype=np.uint8).copy()
            elif sample_width == 2:
                audio_data = np.frombuffer(frames, dtype=np.int16).copy()
            else:
                raise ValueError("รองรับเฉพาะไฟล์เสียง 8-bit หรือ 16-bit เท่านั้น")

            bin_msg = string_to_binary(msg) + '00000000'
            
            if len(bin_msg) > len(audio_data):
                raise ValueError("ข้อความยาวเกินความจุของไฟล์เสียง")
            
            for i in range(len(bin_msg)):
                # ซ่อนในบิตสุดท้าย (LSB)
                audio_data[i] = (audio_data[i] & ~1) | int(bin_msg[i])
            
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audioexample", "output")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"hidden_{os.path.basename(self.selected_audio)}.wav")
            
            with wave.open(output_path, 'wb') as f:
                f.setparams(params)
                f.writeframes(audio_data.tobytes())
            
            if temp_wav and os.path.exists(temp_wav): os.remove(temp_wav)
            self.log_output.append(f"✅ ซ่อนสำเร็จ: {output_path}")
        except Exception as e:
            self.log_output.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")

    def process_extract(self):
        if not self.selected_audio: return
        logger.log("info", "AudioTab: เริ่มกระบวนการถอดข้อความจากไฟล์เสียง")
        try:
            use_path = self.selected_audio
            if not self.selected_audio.lower().endswith('.wav'):
                audio = AudioSegment.from_file(self.selected_audio)
                use_path = "temp_extract.wav"
                audio.export(use_path, format="wav")
            
            with wave.open(use_path, 'rb') as f:
                params = f.getparams()
                frames = f.readframes(f.getnframes())
            
            sample_width = params.sampwidth
            if sample_width == 1:
                audio_data = np.frombuffer(frames, dtype=np.uint8)
            elif sample_width == 2:
                audio_data = np.frombuffer(frames, dtype=np.int16)
            else:
                raise ValueError("รองรับเฉพาะไฟล์เสียง 8-bit หรือ 16-bit เท่านั้น")

            bin_msg = ""
            found = False
            for b in audio_data:
                bin_msg += str(b & 1)
                if len(bin_msg) >= 8 and bin_msg[-8:] == '00000000':
                    found = True
                    break
            
            if not found:
                self.log_output.append("❌ ไม่พบข้อมูลที่ซ่อนอยู่")
            else:
                res = binary_to_string(bin_msg[:-8])
                self.log_output.append(f"🔓 ข้อความที่พบ: {res}")
            if use_path == "temp_extract.wav": os.remove(use_path)
        except Exception as e:
            self.log_output.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")

    def open_output_folder(self):
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audioexample", "output")
        os.makedirs(path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path.lower().endswith(('.wav', '.mp3', '.flac')):
                self.load_audio(path)
