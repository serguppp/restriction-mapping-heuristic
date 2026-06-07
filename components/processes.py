import streamlit as st
import psutil
from components.types import States, map_list_to_string, map_text_to_list, dump_json
import json
import time
import re

import signal

class ProcessManager:
    @staticmethod
    def pause() -> None:
        if st.session_state.process:
            process = psutil.Process(st.session_state.process.pid)
            process.suspend()
            st.session_state.run_state = States.PAUSED.value
            st.session_state.success_msg = "Algorithm paused"
        st.rerun()

    @staticmethod
    def resume() -> None:
        if st.session_state.process:
            process = psutil.Process(st.session_state.process.pid)
            process.resume()
            st.session_state.run_state = States.RUNNING.value
            st.session_state.success_msg = "Algorithm resumed"
        st.rerun()

    @staticmethod
    def stop() -> None:
        if st.session_state.process:
            process = psutil.Process(st.session_state.process.pid)
            if st.session_state.run_state == States.PAUSED.value:
                process.resume()
            process.send_signal(signal.SIGINT)
            st.session_state.process.wait(timeout=2)

            try:
                stdout_data, _ = st.session_state.process.communicate()
                if stdout_data:
                    data = json.loads(stdout_data)
                    if data["status"] == "success":
                        st.session_state.output_m_value = data["m_value"]
                        st.session_state.p_result = map_list_to_string(data["p_result"])
            except Exception:
                pass
            st.session_state.process = None
            st.session_state.log_buffer = ""
            st.session_state.success_msg = "Algorithm stopped"
        st.session_state.run_state = States.IDLE.value
        st.rerun()

    @staticmethod
    def update() -> None:
        if not st.session_state.process or st.session_state.run_state != States.RUNNING.value:
            return
        
        process = st.session_state.process
        q = st.session_state.stderr_queue
        
        while q and not q.empty():
            line = q.get_nowait()
            match = re.search(r"Generation (\d+).*P size\s*=\s*(\d+),\s*Best P\s*=\s*([\d,]+)", line)
            if match:
                st.session_state.output_generation_value = int(match.group(1))
                st.session_state.output_m_value = int(match.group(2))
                st.session_state.p_result = ", ".join(match.group(3).split(","))

        poll = process.poll()
        if poll is not None:
            st.session_state.run_state = States.IDLE.value
            
            stdout_data, _ = process.communicate()
            if stdout_data:
                try:
                    data = json.loads(stdout_data)
                    if data["status"] == "success":
                        st.session_state.output_m_value = data["m_value"]
                        st.session_state.p_result = map_list_to_string(data["p_result"])
                        st.session_state.success_msg = "Algorithm finished successfully!"
                except Exception as e:
                    st.error(f"Error reading result: {e}")
        else:
            time.sleep(0.1)
            st.rerun()