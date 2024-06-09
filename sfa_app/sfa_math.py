import statsmodels.api as sm
import pandas as pd
from pathlib import Path
import numpy as np 
from scipy.optimize import minimize
from scipy.stats import norm
from dataframes import HalfNormal

ln = np.log
f = norm.pdf
F = norm.cdf

def ols(data: pd.DataFrame, y, x, constant = True):
    x = data[x].values.tolist()
    y = data[y].values.tolist()
    if constant:
        x = sm.add_constant(x)

    result = sm.OLS(y, x).fit()
    return result

def cols_deterministic(ols_result):
    return ols_result.params[0] + max(ols_result.resid)

def compute_frontier(distribution: str, data, ols, cols_const, output_str, elasticities_str):
    # We use the ols as a initial guess

    if distribution.lower() == 'half-normal':
        return _compute_frontier_half_normal(data, ols, cols_const, output_str, elasticities_str)
    if distribution.lower() == 'exponential':
        return _compute_frontier_exponential(data, ols, cols_const, output_str, elasticities_str)

def _compute_frontier_half_normal(data: list[float], ols: sm.regression.linear_model.RegressionResults, cols_const: float, output_str: str, elasticities_str: list[str] | str):

    N = len(data)

    def log_likehood_function(epsilon, sigma, lambda_):
        sum_of_epsilon_squared = (epsilon**2).sum()
        # print(1 - F(epsilon*lambda_/sigma))
        # print(epsilon)
        # print(lambda_, sigma)
        log_sum = ln(1 - F(epsilon*lambda_/sigma)).sum()

        # Log-likehood function (Eq 10 in Aigner Lovell Schmidt 1977)
        return N/2 * ln(2/np.pi) - N * ln(sigma) + log_sum - sum_of_epsilon_squared/(2*sigma**2)

    def frontier(params):
        sigma_v = params[0]
        sigma_u = params[1]
        
        lambda_ = sigma_u/sigma_v
        sigma = np.sqrt(sigma_v**2 + sigma_u**2) 
        elasticities = np.array(params[2:])

        # Declare epsilon = y - beta_0 + beta_1 x_1 + ... beta_N x_N, using vector math

        right_hand_side = np.zeros_like(data[output_str]) + elasticities[0]

        # right_hand_side = np.dot(elasticities, data[elasticities_str])

        # beta_1*x_1 + beta_2*x_2 + ... + beta_N*x_N
        for i, elasticity in enumerate(elasticities_str):
            right_hand_side += elasticities[i+1] * data[elasticity]



        epsilon = data[output_str] - right_hand_side

        # Instead of maximizing log-likehood function we minimize negative log-likehood function
        L = -log_likehood_function(epsilon, sigma, lambda_)
        # print("min rn:", L)
        return L

    # Initial guess
    elasticities = ols.params+0.5
    elasticities[0] = cols_const #Replace OLS constant with COLS constant
    sigma_uv_init = np.std(ols.resid) #Same initial gues for sigma_u, sigma_v
    
    # Declare array of initial guesses
    params_init = np.concatenate(([sigma_uv_init, sigma_uv_init], elasticities))

    # Optimize the log-likehood function
    # print("Minimization start")
    bounds = [(0, None), (0, None)] + [(None, None)]*len(params_init[2:]) # Make sure sigma_u, sigma_v are positive
    with np.errstate(divide='ignore', invalid='ignore'):
        result = minimize(frontier, params_init, method='L-BFGS-B', bounds=bounds)
    # print("Minimization end")
    # print(result.x)

    # sigma_v = result.x[0]
    # sigma_u = result.x[1]
    # elasticities = result.x[2:]

    # lambda_ = sigma_u/sigma_v
    # sigma = np.sqrt(sigma_v**2 + sigma_u**2) 

    # # Declare epsilon = y - beta_0 + beta_1 x_1 + ... beta_N x_N, using vector math
    # right_hand_side = np.zeros_like(data[output_str]) + elasticities[0]

    # # beta_1*x_1 + beta_2*x_2 + ... + beta_N*x_N
    # for i, elasticity in enumerate(elasticities_str):
    #     right_hand_side += elasticities[i+1] * data[elasticity]

    # epsilon = data[output_str] - right_hand_side

    # print(sigma_v, sigma_u, elasticities)
    # print("maximization result:", log_likehood_function(epsilon, sigma, lambda_))

    # elasticities = ols.params
    # elasticities[0] = cols_const
    # epsilon = data[output_str] - right_hand_side
    return result.x


def _compute_frontier_exponential(data: list[float], ols: sm.regression.linear_model.RegressionResults, cols_const: float, output_str: str, elasticities_str: list[str] | str):

    N = len(data)

    def log_likehood_function(epsilon: np.ndarray, sigma_v: float, sigma_u: float):
        ll = -ln(sigma_u) + ((sigma_v/sigma_u)**2)/2 + ln(F((-epsilon - (sigma_v**2)/sigma_u)/sigma_v   )) + epsilon/sigma_u
        return ll.sum()

    def frontier(params):
        sigma_v = params[0]
        sigma_u = params[1]

        elasticities = np.array(params[2:])

        # Declare epsilon = y - beta_0 + beta_1 x_1 + ... beta_N x_N, using vector math

        right_hand_side = np.zeros_like(data[output_str]) + cols_const

        # beta_1*x_1 + beta_2*x_2 + ... + beta_N*x_N
        for i, elasticity in enumerate(elasticities_str):
            right_hand_side += elasticities[i] * data[elasticity]

        epsilon = data[output_str] - right_hand_side

        # Instead of maximizing log-likehood function we minimize negative log-likehood function
        L = -log_likehood_function(epsilon, sigma, lambda_)
        # print(L)
        return L

    # Initial guess
    elasticities = ols.params
    elasticities[0] = cols_const #Replace OLS constant with COLS constant
    sigma_uv_init = np.std(ols.resid) #Same initial gues for sigma_u, sigma_v

    # Declare array of initial guesses
    params_init = np.concatenate(([sigma_uv_init, sigma_uv_init], elasticities))

    # Optimize the log-likehood function
    # print("Minimizing start")
    bounds = [(0.001, None), (0.001, None)] + [(None, None)]*len(params_init[2:]) # Make sure sigma_u, sigma_v are positive
    result = minimize(frontier, params_init, method='L-BFGS-B', bounds=bounds)

    sigma_v = result.x[0]
    sigma_u = result.x[1]
    elasticities = result.x[2:]

    lambda_ = sigma_u/sigma_v
    sigma = np.sqrt(sigma_v**2 + sigma_u**2) 

    # Declare epsilon = y - beta_0 + beta_1 x_1 + ... beta_N x_N, using vector math
    right_hand_side = np.zeros_like(data[output_str]) + cols_const

    # beta_1*x_1 + beta_2*x_2 + ... + beta_N*x_N
    for i, elasticity in enumerate(elasticities_str):
        right_hand_side += elasticities[i] * data[elasticity]

    epsilon = data[output_str] - right_hand_side

    # print(sigma_v, sigma_u, elasticities)
    # print("minmization", log_likehood_function(epsilon, sigma, lambda_))

    # elasticities = ols.params
    # elasticities[0] = cols_const
    # epsilon = data[output_str] - right_hand_side
    # print(result.x)
    return result.x


def estimate_inefficiency(estimation, distribution = 'half-normal'):
    if distribution == 'half-normal':
        return _estimate_inefficiency_half_normal(estimation)

def _estimate_inefficiency_half_normal(estimation: HalfNormal, which = 'all'):
    # Assumes mu_star has been set
    ratio = estimation.mu_star/estimation.sigma_star

    if which == 'all':
        conditional_mean_inefficiency = estimation.mu_star + estimation.sigma_star * f(-ratio)/F(ratio)
        conditional_mode_inefficiency = np.maximum(estimation.mu_star, 0)
        # print(np.exp(-conditional_mean_inefficiency))
        return conditional_mean_inefficiency, conditional_mode_inefficiency

    elif which == 'mode':
        conditional_mode_inefficiency = np.maximum(estimation.mu_star, 0)
        return conditional_mode_inefficiency
    
    else: # mean
        conditional_mean_inefficiency = estimation.mu_star + estimation.sigma_star * f(-ratio)/F(ratio)
        return conditional_mean_inefficiency
    
def estimate_technical_efficiency(estimation: HalfNormal, u, exp = True):
    # Technical efficiency is observed output/max possible output
    print("!")
    if isinstance(u, tuple):
        TE = []
        if exp:
            for inef in u:
                TE.append(np.exp(-inef))
        else:
            for inef in u:
                TE.append((estimation.rhs - inef)/estimation.rhs)

    else:
        if exp: 
            TE = np.exp(-u)
        else:
            TE = (estimation.rhs - u)/estimation.rhs

        np.divide()

    return TE

if __name__ == "__main__":
    app_dir = Path(__file__).parent
    data_dir = app_dir.parent / 'example_data'
    elsalvador = [f for f in data_dir.glob('**/*') if f.name == "elsalvador.csv"][0]
    data = pd.read_csv(elsalvador)
    r = ols(data, "loutput", ["fam_electricidad", "fam_letrinas"])
    # print(r.summary())