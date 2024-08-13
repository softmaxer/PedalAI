from __future__ import annotations

import os
from typing import Iterable, List
import uuid
from pydantic import BaseModel

from session.audio_source import AudioSource
from pedalboard import Plugin
import pickle
from mistralai.models.chat_completion import ToolCall

DEAFAULT_SAMPLE_RATE = 44100
DEFAULT_NUM_CHANNELS = 2


class PluginsData(BaseModel):
    start: float
    end: float
    plugins: List[ToolCall]


class Track:
    def __init__(self, path: str = "./pedalAi/sessions", **kwargs) -> None:
        self.plugins: Iterable[Plugin] = []
        self.id = kwargs.get("session_id")
        if self.id is None:
            self.id = "session_{}".format(str(uuid.uuid4()))
        self.save_path = os.path.join(path, self.id)

    def save(self) -> None:
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        if self.original:
            with open(self.original.path, "wb") as f:
                f.write(self.original.contents)

        if self.last_modified:
            print("In here")
            with open(self.last_modified.path, "wb") as f:
                f.write(self.last_modified.contents)

        if len(self.plugins) > 0:  # type: ignore
            with open(os.path.join(self.save_path, "plugins.pkl"), "wb") as f:
                pickle.dump(self.plugins, f)

    def add_track(self, audio_source: AudioSource) -> None:
        self.original = audio_source

    def add_plugin(self, plugin: Plugin) -> None:
        self.plugins.append(plugin)  # type: ignore

    @staticmethod
    def load(session_id: str) -> Track:
        path = os.path.join("./pedalAi/sessions", session_id)
        session = Track("./pedalAi/sessions", session_id=session_id)
        original_path = os.path.join(path, "original.wav")
        modified_path = os.path.join(path, "modified.wav")

        if os.path.exists(original_path):
            with open(original_path, "rb") as f:
                samples = f.read()

                original_track = AudioSource(
                    "original",
                    0.0,
                    "",
                    samples,
                    original_path,
                )
                session.original = original_track

        if os.path.exists(modified_path):
            with open(modified_path, "rb") as f:
                samples = f.read()

                modified_track = AudioSource(
                    "original",
                    0.0,
                    "",
                    samples,
                    modified_path,
                )
                print("if the next print prints, that's not the error")
                session.last_modified = modified_track
                print("next print")

        if os.path.exists(os.path.join(session.save_path, "plugins.pkl")):
            with open(
                os.path.join(session.save_path, "plugins.pkl"), "rb"
            ) as f:
                session.plugins = pickle.load(f)

        return session

    @property
    def last_modified(self) -> AudioSource:
        return self._last_modified

    @last_modified.setter
    def last_modified(self, t: AudioSource) -> None:
        self._last_modified = t

    @property
    def original(self) -> AudioSource:
        return self._original

    @original.setter
    def original(self, t: AudioSource) -> None:
        self._original = t

    def rollback(self) -> None:
        del self.plugins[-1]  # type: ignore
