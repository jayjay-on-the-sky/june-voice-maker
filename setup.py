from setuptools import setup

APP = ['JuneVoiceMaker.py']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['TTS', 'torch', 'gradio', 'pydub'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
