import pandas as pd


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
