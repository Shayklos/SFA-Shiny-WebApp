import statsmodels.api as sm
import pandas as pd
from pathlib import Path

def ols(data: pd.DataFrame, y, x, constant = True):
    x = data[x].values.tolist()
    y = data[y].values.tolist()
    if constant:
        x = sm.add_constant(x)

    result = sm.OLS(y, x).fit()
    return result

def cols_deterministic(ols_result):
    print(ols_result.params[0], max(ols_result.resid))
    print(ols_result.params)
    return ols_result.params[0] + max(ols_result.resid)

if __name__ == "__main__":
    app_dir = Path(__file__).parent
    data_dir = app_dir.parent / 'example_data'
    elsalvador = [f for f in data_dir.glob('**/*') if f.name == "elsalvador.csv"][0]
    data = pd.read_csv(elsalvador)
    r = ols(data, "loutput", ["fam_electricidad", "fam_letrinas"])
    print(r.params)