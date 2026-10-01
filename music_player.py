"""Voice-command integration for local audio files; Google recognition is online."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

AUDIO_SUFFIXES={'.mp3','.wav','.ogg','.flac','.m4a'}
class MusicError(ValueError):pass

def normalize(text: str) -> str:
    return ' '.join(re.findall(r'\w+',text.casefold()))

def catalog(directory: Path) -> dict[str,Path]:
    if not directory.is_dir():raise MusicError('Music directory does not exist')
    songs={}
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES:
            name=normalize(path.stem)
            if name in songs:raise MusicError(f'Ambiguous normalized song name: {name}')
            songs[name]=path.resolve()
    if not songs:raise MusicError('No supported audio files found')
    return songs

def select_song(command: str, songs: dict[str,Path]) -> Path:
    query=normalize(command)
    if query.startswith('play '):query=query[5:]
    if not query:raise MusicError('No song name was recognized')
    if query in songs:return songs[query]
    candidates=[path for name,path in songs.items() if re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',query)]
    if len(candidates)!=1:raise MusicError('Song not found or command is ambiguous')
    return candidates[0]

def recognize(seconds: float) -> str:
    try:import speech_recognition as sr
    except ImportError as error:raise MusicError('Install requirements-voice.txt for microphone input') from error
    recognizer=sr.Recognizer();recognizer.operation_timeout=15
    try:
        with sr.Microphone() as source:
            print('Which song would you like to hear?',file=sys.stderr)
            recognizer.adjust_for_ambient_noise(source,duration=0.5)
            audio=recognizer.listen(source,timeout=10,phrase_time_limit=seconds)
        return recognizer.recognize_google(audio)
    except (sr.UnknownValueError,sr.WaitTimeoutError) as error:raise MusicError('No intelligible command was captured') from error
    except sr.RequestError as error:raise MusicError('Online recognition failed; try --command for offline input') from error
    except OSError as error:raise MusicError('Microphone/audio backend is unavailable') from error

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--music-dir',type=Path,required=True);parser.add_argument('--command',help='Typed command; no recognition/network needed');parser.add_argument('--dry-run',action='store_true',help='Resolve without playing');parser.add_argument('--seconds',type=float,default=5)
    args=parser.parse_args(argv)
    if not 0<args.seconds<=30:parser.error('--seconds must be in (0,30]')
    try:
        songs=catalog(args.music_dir)
        command=args.command if args.command is not None else recognize(args.seconds)
        song=select_song(command,songs)
        if args.dry_run:print(json.dumps({'song':song.name,'path':str(song),'recognition':'typed-offline' if args.command is not None else 'google-online'}));return 0
        player=shutil.which('ffplay')
        if not player:raise MusicError('Install FFmpeg (ffplay) or use --dry-run')
        result=subprocess.run([player,'-nodisp','-autoexit','-loglevel','error',str(song)],check=False)
        if result.returncode:raise MusicError('Audio player failed')
        return 0
    except (MusicError,OSError) as error:print(f'Error: {error}',file=sys.stderr);return 1
    except KeyboardInterrupt:return 130

if __name__=='__main__':raise SystemExit(main())
