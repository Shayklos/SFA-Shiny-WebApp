from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
data_dir = app_dir.parent / 'example_data'
data_files = [f.name for f in data_dir.glob('**/*') if f.is_file()]

tips = pd.read_csv(data_dir / "tips.csv")
