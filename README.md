# MyMusi

Historical speech-command music-player experiment. The maintained CLI selects local audio files from a directory and plays them with FFmpeg's `ffplay`. Voice input uses SpeechRecognition's Google service and **requires network access**. The earlier notebook also used online gTTS for spoken prompts. This is an API integration, not a trained speech or music model.

## Reproduce without microphone or online services

Use Python 3.11+:

```bash
python3 scripts/create_sample.py
python3 music_player.py --music-dir music --command 'play sample tone' --dry-run
python3 music_player.py --music-dir music --command 'play sample tone'
```

The sample script generates an original sine-wave tone locally. Install FFmpeg for actual playback; dry-run requires only Python. Supply your own audio files for a real library. Names are resolved case-insensitively; ambiguous or missing songs fail clearly instead of accessing uninitialized matches.

## Voice input

Create a virtual environment and install `requirements-voice.txt`. PyAudio needs PortAudio/system audio development prerequisites; see the [SpeechRecognition installation guide](https://pypi.org/project/SpeechRecognition/). Then omit `--command` to record a microphone command. Capture and online recognition have time bounds. This mode sends captured speech to an external service.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-voice.txt
python music_player.py --music-dir /path/to/your/music
```

The original notebook and audio files remain historical artifacts. Their presence does not grant redistribution rights to third-party recordings; the reproducible example uses the generated tone. Notebook dependencies also include `gTTS`; the maintained CLI uses text prompts and does not need it or `playsound`.

Run `python3 -m unittest discover -s tests -v`. CI verifies typed command selection, ambiguous/error cases, and a fresh CLI process. Microphone capture, online recognition, and audible playback require a machine with those devices/services and are not certified by CI.
