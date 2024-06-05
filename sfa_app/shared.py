from pathlib import Path

import pandas as pd

import markdown
from mdx_math import MathExtension

from auxiliar import get_content

app_dir = Path(__file__).parent
data_dir = app_dir.parent / 'example_data'
data_files = [f for f in data_dir.glob('**/*') if f.suffix in {'.txt', '.csv'}]
md_files =[f for f in data_dir.glob('**/*') if f.suffix in {'.md'}]
mds ={md.name:get_content(md) for md in md_files}

tips = pd.read_csv(data_dir / "tips.csv")

md__ = markdown.Markdown(extensions=[MathExtension(enable_dollar_delimiter=True)])
md_render = md__.convert
