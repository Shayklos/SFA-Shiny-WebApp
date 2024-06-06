import statsmodels.api as sm
import pandas as pd
from pathlib import Path
import numpy as np 
from scipy.optimize import minimize
from scipy.stats import norm

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

def compute_frontier(ols, distribution: str):
    # We use the ols as a initial guess

    if distribution.lower() == 'half-normal':
        return _compute_frontier_half_normal(ols)

def _compute_frontier_half_normal(data: list[float], ols, cols_const: float, output_str: str, elasticities_str: list[str] | str):

    N = len(data)
    ln = np.log
    f = norm.pdf
    F = norm.cdf

    def frontier(params):
        sigma_v = params[0]
        sigma_u = params[1]

        lambda_ = sigma_u/sigma_v
        sigma = np.sqrt(sigma_v**2 + sigma_u**2) 
        elasticities = np.array(params[2:])

        # Declare epsilon = y - beta_0 + beta_1 x_1 + ... beta_N x_N, using vector math

        right_hand_side = np.zeros_like(data[output_str]) + cols_const

        # beta_1*x_1 + beta_2*x_2 + ... + beta_N*x_N
        for i, elasticity in enumerate(elasticities_str):
            right_hand_side += elasticities[i] * data[elasticity]

        epsilon = data[output_str] - right_hand_side

        sum_of_epsilon_squared = epsilon.sum()
        log_sum = 0
        
        for e in epsilon:
            log_sum += ln(1 - F(e*lambda_/sigma))


        # Log-likehood function (Eq 10 in Aigner Lovell Schmidt 1977)
        L = N * ln( np.sqrt(2/np.pi) ) - N * ln(sigma) + log_sum - sum_of_epsilon_squared/(2*sigma**2)

        # Instead of maximizing log-likehood function we minimize negative log-likehood function
        return -L


if __name__ == "__main__":
    app_dir = Path(__file__).parent
    data_dir = app_dir.parent / 'example_data'
    elsalvador = [f for f in data_dir.glob('**/*') if f.name == "elsalvador.csv"][0]
    data = pd.read_csv(elsalvador)
    r = ols(data, "loutput", ["fam_electricidad", "fam_letrinas"])
    # print(r.summary())