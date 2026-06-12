import json
import queue
import re
import signal
import time
from subprocess import Popen

import psutil
import streamlit as st

from components.task_state import TaskState
from components.types import States, map_list_to_string


class Process:
    def __init__(
        self,
        task_state: TaskState,
        run_state: States = States.IDLE,
        process: Popen | None = None,
        queue: queue.Queue | None = None,
    ):
        self.process = process
        self.run_state = run_state
        self.queue = queue
        self.task_state = task_state

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
        self.task_state.success_msg = message
        st.rerun()

    def read_queue_and_update_output(self) -> None:
        q = self.queue

        while q and not q.empty():
            line = q.get_nowait()
            match = re.search(
                r"Generation (\d+),\s*Time:\s*([\d.e+-]+).*P size\s*=\s*(\d+),\s*Best P\s*=\s*([\d,]+)",
                line,
            )

            if match:
                generation = int(match.group(1)) + 1
                current_time = round(float(match.group(2)), 2)
                m = int(match.group(3))
                p_result = ", ".join(match.group(4).split(","))

                self.task_state.set_results(generation, current_time, m, p_result)

    def read_json_and_update_output(self) -> None:
        if self.process:
            try:
                stdout_data, _ = self.process.communicate()
                data = json.loads(stdout_data)
                if data["status"] == "success":
                    generation = int(data["generation"])
                    m = int(data["m_value"])
                    current_time = round(float(data["time"]), 2)
                    p_result = map_list_to_string(data["p_result"])

                    self.task_state.set_results(generation, current_time, m, p_result)
                    self.task_state.success_msg = "Algorithm finished successfully!"
            except Exception as e:
                st.error(f"Error reading result: {e}")

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

        if self.process and self.process.poll() is not None:
            self.read_json_and_update_output()
            self.process = None
            self.run_state = States.IDLE
            st.rerun()
        else:
            time.sleep(0.1)
            st.rerun()
