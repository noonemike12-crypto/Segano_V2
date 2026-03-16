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

class AudioTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_audio = None
        self.capacity = 0
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- ส่วนจัดการไฟล์เสียง ---
        audio_group = QGroupBox("🎵 การจัดการไฟล์เสียง (Audio Management)")
        audio_layout = QVBoxLayout()
        
        file_selection = QHBoxLayout()
        self.example_selector = QComboBox()
        self.example_selector.setPlaceholderText("เลือกไฟล์เสียงตัวอย่าง...")
        self.example_selector.currentIndexChanged.connect(self.load_example_audio)
        file_selection.addWidget(self.example_selector, 1)
        
        self.browse_btn = QPushButton("🔍 เลือกไฟล์เสียง...")
        self.browse_btn.clicked.connect(self.browse_audio)
        file_selection.addWidget(self.browse_btn, 1)
        audio_layout.addLayout(file_selection)
        
        self.path_label = QLabel("ยังไม่ได้เลือกไฟล์")
        self.path_label.setAlignment(Qt.AlignCenter)
        self.path_label.setStyleSheet("border: 2px dashed #4a5568; border-radius: 10px; padding: 10px;")
        audio_layout.addWidget(self.path_label)
        
        playback_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶️ เล่น (Play)")
        self.play_btn.clicked.connect(self.play_audio)
        self.stop_btn = QPushButton("⏹️ หยุด (Stop)")
        self.stop_btn.clicked.connect(self.stop_audio)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.stop_btn)
        audio_layout.addLayout(playback_layout)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # --- ส่วนข้อความและความจุ ---
        message_group = QGroupBox("💬 ข้อความและความจุ (Message & Capacity)")
        message_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("พิมพ์ข้อความลับที่นี่...")
        self.message_input.textChanged.connect(self.update_capacity)
        message_layout.addWidget(self.message_input, 2)
        
        self.capacity_info = QLabel("ความจุ: N/A\nใช้ไป: 0 บิต")
        self.capacity_info.setAlignment(Qt.AlignCenter)
        self.capacity_info.setStyleSheet("background-color: #1a222d; border-radius: 10px; padding: 10px;")
        message_layout.addWidget(self.capacity_info, 1)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)

        # --- ส่วนดำเนินการและผลลัพธ์ ---
        action_group = QGroupBox("🚀 ดำเนินการ (Actions)")
        action_layout = QVBoxLayout()
        
        btns = QHBoxLayout()
        self.hide_btn = QPushButton("🔒 ซ่อนข้อความ")
        self.hide_btn.setObjectName("primaryBtn")
        self.hide_btn.clicked.connect(self.process_hide)
        
        self.extract_btn = QPushButton("🔓 ถอดข้อความ")
        self.extract_btn.setObjectName("secondaryBtn")
        self.extract_btn.clicked.connect(self.process_extract)
        
        self.folder_btn = QPushButton("📁 โฟลเดอร์ผลลัพธ์")
        self.folder_btn.clicked.connect(self.open_output_folder)
        
        btns.addWidget(self.hide_btn)
        btns.addWidget(self.extract_btn)
        btns.addWidget(self.folder_btn)
        action_layout.addLayout(btns)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("บันทึกการทำงานจะแสดงที่นี่...")
        action_layout.addWidget(self.log_output)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        self.load_examples()

    def load_examples(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        example_dir = os.path.join(base_dir, "audioexample")
        if os.path.exists(example_dir):
            files = [f for f in os.listdir(example_dir) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
            self.example_selector.addItems(files)

    def load_audio(self, path):
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
            for b in audio_data:
                bin_msg += str(b & 1)
                if len(bin_msg) >= 8 and bin_msg[-8:] == '00000000': break
            
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
