import json
import queue
import re
import signal
import time
from subprocess import Popen

import psutil
import streamlit as st

from components.types import States, map_list_to_string


class Process:
    def __init__(
        self,
        run_state: States = States.IDLE,
        process: Popen | None = None,
        queue: queue.Queue | None = None,
    ):
        self.process = process
        self.run_state = run_state
        self.queue = queue

    def set(self, process: Popen, run_state: States, queue: queue.Queue) -> None:
        self.process = process
        self.run_state = run_state
        self.queue = queue

    def handle(self, run_state: States, message: str) -> None:
        if self.process is not None:
            psutil_process = psutil.Process(self.process.pid)
            if run_state == States.PAUSED:
                psutil_process.suspend()
            elif run_state == States.RUNNING:
                psutil_process.resume()
            elif run_state == States.IDLE:
                if self.run_state == States.PAUSED:
                    psutil_process.resume()

                psutil_process.send_signal(signal.SIGINT)
                try:
                    psutil_process.wait(timeout=2)
                except Exception:
                    self.process.kill()

                try:
                    if self.process is not None:
                        if self.process.stdout is not None:
                            self.process.stdout.close()
                        if self.process.stderr is not None:
                            self.process.stderr.close()
                except Exception:
                    pass
                self.process = None

        self.run_state = run_state
        st.session_state.success_msg = message
        st.rerun()

    def read_queue_and_update_output(self) -> None:
        q = self.queue

        while q and not q.empty():
            line = q.get_nowait()
            match = re.search(
                r"Generation (\d+).*P size\s*=\s*(\d+),\s*Best P\s*=\s*([\d,]+)",
                line,
            )

            if match:
                st.session_state.output_generation_value = int(match.group(1)) + 1
                st.session_state.output_m_value = int(match.group(2))
                st.session_state.p_result = ", ".join(match.group(3).split(","))

    def pause(self) -> None:
        self.handle(States.PAUSED, "Algorithm paused")

    def resume(self) -> None:
        self.handle(States.RUNNING, "Algorithm resumed")

    def stop(self) -> None:
        self.handle(States.IDLE, "Algorithm stopped")

    def update(self) -> None:
        if not self.process or self.run_state != States.RUNNING:
            return

        self.read_queue_and_update_output()

        poll = self.process.poll()
        if poll is not None:
            self.run_state = States.IDLE
            try:
                stdout_data, _ = self.process.communicate()
                data = json.loads(stdout_data)
                if data["status"] == "success":
                    st.session_state.output_m_value = data["m_value"]
                    st.session_state.p_result = map_list_to_string(data["p_result"])
                    st.session_state.success_msg = "Algorithm finished successfully!"
            except Exception as e:
                st.error(f"Error reading result: {e}")
            self.process = None
            st.rerun()
        else:
            time.sleep(0.1)
            st.rerun()
