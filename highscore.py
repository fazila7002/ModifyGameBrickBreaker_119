"""Simpan & baca high score ke file highscore.json (di folder yang sama dengan game)."""
import json
import os

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'highscore.json')


def load():
    try:
        with open(FILE, encoding='utf-8') as f:
            return int(json.load(f).get('high_score', 0))
    except (OSError, ValueError, AttributeError):
        return 0


def save(score):
    try:
        with open(FILE, 'w', encoding='utf-8') as f:
            json.dump({'high_score': int(score)}, f)
    except OSError:
        pass
