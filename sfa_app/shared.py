from pathlib import Path

import pandas as pd

import markdown
from mdx_math import MathExtension

app_dir = Path(__file__).parent
data_dir = app_dir.parent / 'example_data'
data_files = [f for f in data_dir.glob('**/*') if f.is_file()]

tips = pd.read_csv(data_dir / "tips.csv")

md = markdown.Markdown(extensions=[MathExtension(enable_dollar_delimiter=True)])
md_render = md.convert