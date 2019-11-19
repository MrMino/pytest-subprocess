# -*- coding: utf-8 -*-
import io
import threading
import typing

import pytest  # type: ignore

OPTIONAL_TEXT = typing.Union[str, bytes, None]

def _ensure_hashable(
    input: typing.Union[typing.List[str], typing.Tuple[str], str]
) -> typing.Union[typing.Tuple[str], str]: ...

class FakePopen:
    __command: typing.Union[typing.List[str], typing.Tuple[str], str]
    stdout: typing.Optional[io.BytesIO]
    stderr: typing.Optional[io.BytesIO]
    returncode: typing.Optional[int]
    __stdout: OPTIONAL_TEXT
    __stderr: OPTIONAL_TEXT
    __returncode: typing.Optional[int]
    __wait: typing.Optional[float]
    __thread: typing.Optional[threading.Thread]
    def __init__(
        self,
        command: typing.Union[typing.Tuple[str], str],
        stdout: OPTIONAL_TEXT = None,
        stderr: OPTIONAL_TEXT = None,
        returncode: int = 0,
        wait: typing.Optional[float] = None,
    ) -> None: ...
    def communicate(
        self, input: OPTIONAL_TEXT = ..., timeout: typing.Optional[float] = ...,
    ) -> typing.Tuple[typing.Any, typing.Any]: ...
    def poll(self) -> None: ...
    def wait(self, timeout: typing.Optional[float] = None) -> int: ...
    def configure(self, **kwargs: typing.Optional[typing.Dict]) -> None: ...
    @staticmethod
    def _prepare_buffer(
        input: typing.Union[str, bytes, None],
        io_base: typing.Optional[io.BytesIO] = None,
    ) -> io.BytesIO: ...
    def _wait(self, wait_period: float) -> None: ...
    def run_thread(self) -> None: ...

class ProcessNotRegisteredError(Exception): ...

class ProcessDispatcher:
    process_list: typing.List["Process"]
    built_in_popen: typing.Optional[typing.Callable]
    _allow_unregistered: bool
    @classmethod
    def register(cls, process: "Process") -> None: ...
    @classmethod
    def deregister(cls, process: "Process") -> None: ...
    @classmethod
    def dispatch(
        cls,
        command: typing.Union[typing.Tuple[str], str],
        **kwargs: typing.Optional[typing.Dict]
    ) -> FakePopen: ...
    @classmethod
    def allow_unregistered(cls, allow: bool) -> None: ...

class Process:
    processes: typing.Dict[typing.Union[str, typing.Tuple[str]], typing.Dict]
    def __init__(self) -> None: ...
    def register_subprocess(
        self,
        command: typing.Union[typing.List[str], typing.Tuple[str], str],
        stdout: OPTIONAL_TEXT = None,
        stderr: OPTIONAL_TEXT = None,
        returncode: int = 0,
        wait: typing.Optional[float] = None,
    ) -> None: ...
    def __enter__(self) -> "Process": ...
    def __exit__(self, *args: typing.List, **kwargs: typing.Dict) -> None: ...
    def allow_unregistered(cls, allow: bool) -> None: ...
    @classmethod
    def context(cls) -> "Process": ...

@pytest.fixture
def fake_process() -> Process: ...
