# -*- coding: utf-8 -*-
import io
import subprocess

import pytest


def _ensure_hashable(input):
    if isinstance(input, list):
        return tuple(input)
    return input


class FakePopen:
    """The base class that fakes the real subprocess"""

    stdout = None
    stderr = None

    def __init__(self, command, stdout=None, stderr=None, returncode=0):
        self.__command = command
        self.__stdout = stdout
        self.__stderr = stderr
        self.returncode = returncode

    def communicate(self, input=None, timeout=None):
        return (
            self.stdout.getvalue() if self.stdout else None,
            self.stderr.getvalue() if self.stderr else None,
        )

    def poll(self):
        return self.returncode

    def configure(self, **kwargs):
        if kwargs.get("stdout") == subprocess.PIPE:
            self.stdout = self._prepare_buffer(self.__stdout)
        stderr = kwargs.get("stderr")
        if stderr == subprocess.STDOUT:
            self.stdout = self._prepare_buffer(self.__stderr, self.stdout)
        elif stderr == subprocess.PIPE:
            self.stderr = self._prepare_buffer(self.__stderr)

    @staticmethod
    def _prepare_buffer(input, io_base=None):
        if io_base is None:
            io_base = io.BytesIO()
        if isinstance(input, (list, tuple)):
            io_base.write(
                b"\n".join(
                    line.encode() if isinstance(line, str) else line for line in input
                )
            )

        if isinstance(input, str):
            io_base.write(input.encode())

        return io_base


class ProcessNotRegisteredError(Exception):
    """
    Raised when the attempted command wasn't registered before.
    Use `fake_process.allow_unregistered(True)` if you want to use real subprocess.
    """


class ProcessDispatcher:
    """Main class for handling processes."""

    process_list = []
    built_in_popen = None
    _allow_unregistered = False

    @classmethod
    def register(cls, process):
        if not cls.process_list:
            cls.built_in_popen = subprocess.Popen
            subprocess.Popen = cls.dispatch
        cls.process_list.append(process)

    @classmethod
    def deregister(cls, process):
        cls.process_list.remove(process)
        if not cls.process_list:
            subprocess.Popen = cls.built_in_popen
            cls.built_in_popen = None

    @classmethod
    def dispatch(cls, command, **kwargs):
        command = _ensure_hashable(command)
        process = next(
            (
                proc.processes.get(command)
                for proc in reversed(cls.process_list)
                if command in proc.processes
            ),
            None,
        )

        if process is None:
            if not cls._allow_unregistered:
                raise ProcessNotRegisteredError(
                    "The process '{}' was not registered.".format(
                        command if isinstance(command, str) else " ".join(command)
                    )
                )
            else:
                return cls.built_in_popen(command, **kwargs)

        result = FakePopen(**process)
        result.configure(**kwargs)
        return result

    @classmethod
    def allow_unregistered(cls, allow):
        cls._allow_unregistered = allow


class Process:
    """Class responsible for tracking the processes"""

    def __init__(self):
        self.processes = dict()

    def register_subprocess(self, command, stdout=None, stderr=None, returncode=0):
        command = _ensure_hashable(command)
        self.processes[command] = {
            "command": command,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
        }

    def __enter__(self):
        ProcessDispatcher.register(self)
        return self

    def __exit__(self, *args, **kwargs):
        ProcessDispatcher.deregister(self)

    def allow_unregistered(cls, allow):
        ProcessDispatcher.allow_unregistered(allow)

    @classmethod
    def context(cls):
        return cls()


@pytest.fixture
def fake_process():
    with Process() as process:
        yield process
