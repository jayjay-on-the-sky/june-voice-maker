import gradio as gr
from TTS.api import TTS
from pydub import AudioSegment
import os
import tempfile

# Load model
tts = TTS(model_name="trungtv/tts-vi", progress_bar=False, gpu=False)

speakers = tts.speakers
speaker_options = {0: "Nữ", 1: "Nam"} if speakers and len(speakers) >= 2 else {0: "Mặc định"}

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
    mp3_path = tmp_wav.name.replace(".wav", ".mp3")
    louder.export(mp3_path, format="mp3")
    os.remove(tmp_wav.name)
    return mp3_path

def process(text, file, voice, speed, volume):
    if file is not None:
        text = file.read().decode("utf-8")
    speaker_id = int(voice)
    return synthesize(text, speaker_id, speed, volume)

with gr.Blocks(title="June Voice Maker") as demo:
    gr.Markdown("# 🎙️ June Voice Maker\nNhập văn bản hoặc upload file để tạo giọng nói tiếng Việt (.mp3)")

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
    output = gr.Audio(label="Tải file .mp3", type="filepath")

    btn.click(fn=process,
              inputs=[txt, file, voice, speed, volume],
              outputs=output)

demo.launch()
