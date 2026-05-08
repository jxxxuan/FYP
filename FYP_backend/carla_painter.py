'''
File: carla_painter.py
Author: Minjun Xu (mjxu96@outlook.com)
File Created: Monday, 7th October 2019 7:17:32 pm
'''

from websocket import create_connection
import logging
import json

import json
import threading
import websocket

class CarlaPainter:
    def __init__(self, host="localhost", port=8089):
        self._url = f"ws://{host}:{port}"
        self._lock = threading.Lock()
        self._ws = websocket.WebSocket()
        self._connect()

    def _connect(self):
        try:
            self._ws.connect(self._url)
            print(f"[CarlaPainter] Connected to {self._url}")
        except Exception as e:
            print(f"[CarlaPainter] Connection failed: {e}")

    def _send(self, data: dict):
        with self._lock:
            try:
                self._ws.send(json.dumps(data))
            except Exception:
                self._connect()
                self._ws.send(json.dumps(data))

    def draw_polylines(self, polylines: list):
        """polylines: [ [(x,y,z),(x,y,z),...], ... ]"""
        flat = [[c for pt in pl for c in pt] for pl in polylines]
        self._send({"polylines": flat})

    def draw_points(self, points: list):
        """points: [(x,y,z), ...]"""
        self._send({"points": [list(p) for p in points]})

    def draw_arrows(self, starts: list, ends: list):
        """starts/ends: [(x,y,z), ...]"""
        self._send({"arrows": [
            {"start": list(s), "end": list(e)}
            for s, e in zip(starts, ends)
        ]})

    def draw_texts(self, texts: list, positions: list):
        """texts: ['str',...], positions: [(x,y,z),...]"""
        self._send({"texts": [
            {"content": t, "position": list(p)}
            for t, p in zip(texts, positions)
        ]})

    def close(self):
        self._ws.close()