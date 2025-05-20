import os
import gradio as gr
from TTS.api import TTS
from pydub import AudioSegment
import tempfile
from datetime import datetime

# 📥 Tự động tải model về nếu chưa có
MODEL_PATH = "models/trungtv_tts_vi"
MODEL_NAME = "trungtv/tts-vi"

if not os.path.exists(MODEL_PATH):
    print("🔁 Đang tải mô hình từ Hugging Face...")
    tts = TTS(model_name=MODEL_NAME, progress_bar=True, gpu=False)
    tts.save_model(MODEL_PATH)
    print("✅ Tải mô hình thành công!")
else:
    print("✅ Đã có mô hình, đang khởi động...")
    tts = TTS(model_path=MODEL_PATH, progress_bar=False, gpu=False)

# 🎙️ Lấy danh sách speaker
speakers = tts.speakers
speaker_options = {0: "Nữ", 1: "Nam"} if speakers and len(speakers) >= 2 else {0: "Mặc định"}

# 🔊 Hàm xử lý TTS
def synthesize(text, speaker_id, speed, volume_db):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        tts.tts_to_file(
            text=text,
            speaker=speaker_id,
            file_path=tmp_wav.name,
            speed=speed,
        )
    audio = AudioSegment.from_wav(tmp_wav.name)
    louder = audio + volume_db

    # 📁 Tạo thư mục output nếu chưa có
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 📝 Đặt tên file theo thời gian
    filename = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    mp3_path = os.path.join(output_dir, filename)

    louder.export(mp3_path, format="mp3")
    os.remove(tmp_wav.name)
    return mp3_path

# 📂 Hàm xử lý input
def process(text, file, voice, speed, volume):
    if file is not None:
        text = file.read().decode("utf-8")
    speaker_id = int(voice)
    return synthesize(text, speaker_id, speed, volume)

# 🚀 Giao diện Gradio
with gr.Blocks(title="June Voice Maker") as demo:
    gr.Markdown("# 🎙️ June Voice Maker\nTạo giọng nói tiếng Việt từ văn bản (.mp3)")

    with gr.Row():
        txt = gr.Textbox(label="Nhập văn bản", lines=6)
        file = gr.File(label="Hoặc chọn file .txt", file_types=[".txt"])

    with gr.Row():
        voice = gr.Radio(choices=[str(k) for k in speaker_options.keys()],
                         label="Chọn giọng", value="0",
                         info="0: Nữ, 1: Nam")
        speed = gr.Slider(0.5, 2.0, value=1.0, label="Tốc độ nói")
        volume = gr.Slider(-10, 10, value=0, label="Âm lượng (dB)")

    btn = gr.Button("Tạo giọng nói")
    output = gr.Audio(label="Nghe & Tải về", type="filepath")

    btn.click(fn=process,
              inputs=[txt, file, voice, speed, volume],
              outputs=output)

demo.launch()
