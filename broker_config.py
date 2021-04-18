from __future__ import annotations
from typing import NamedTuple
from ast import literal_eval


class Config(NamedTuple):
    """A helper class to allow for auto-complete when writing in an IDE."""
    host: str
    port: int
    username: str
    password: str
    topic: str

    @staticmethod
    def from_file(path: str) -> Config:
        with open(path, "r") as file:
            raw = file.read()
        try:
            parsed = literal_eval(raw)
            return Config(**parsed)
        except (SyntaxError, TypeError) as e:
            raise RuntimeError("Invalid configuration file!") from e

    def to_file(self, path: str) -> None:
        serialized = str(self._asdict())
        with open(path, "w") as file:
            file.write(serialized)

