from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
data_dir = app_dir.parent / 'example_data'

tips = pd.read_csv(data_dir / "tips.csv")
