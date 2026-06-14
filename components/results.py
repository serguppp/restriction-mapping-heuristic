import json
from dataclasses import asdict
from datetime import datetime

import pandas as pd
import streamlit as st

from components.constants import RESULTS_DIR
from components.task_state import TaskState


def get_results_df(
    p_size: int, results: list[dict[str, int | str | float]]
) -> pd.DataFrame:
    df = pd.DataFrame(results)

    df["Target value (P size)"] = p_size

    df = df.rename(
        columns={
            "m": "Current value (m)",
            "time": "Time (seconds)",
            "generation": "Generation",
        }
    )
    df = df.reindex(
        columns=[
            "Generation",
            "Time (seconds)",
            "Target value (P size)",
            "Current value (m)",
        ]
    )

    return df


def save_results(task_state: TaskState) -> None:
    try:
        if not task_state.results:
            st.toast("No results to save")
            return

        data = asdict(task_state)
        data.pop("success_msg")
        json_string = json.dumps(data)

        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"results_{suffix}.json"
        json_path = RESULTS_DIR / file_name

        json_path.write_text(json_string, encoding="utf-8")
        st.toast("Results saved")

    except Exception as e:
        st.toast(f"Error saving results: {e}")


def read_results() -> list[tuple[str, TaskState]]:
    results = []

    for file in sorted(RESULTS_DIR.glob("*.json")):
        try:
            json_string = file.read_text(encoding="utf-8")
            data = json.loads(json_string)
            data.pop("success_msg", None)
            task_state = TaskState(**data)
            results.append((file.name, task_state))
        except Exception as e:
            print(f"Error reading file {file.name}: {e}")
    return results


def delete_results(file_name: str | None = None) -> None:
    try:
        if file_name:
            file_path = RESULTS_DIR / file_name
            if file_path.exists():
                file_path.unlink()
        else:
            for file in RESULTS_DIR.glob("*.json"):
                file.unlink()
    except Exception as e:
        print(f"Error deleting file: {e}")
