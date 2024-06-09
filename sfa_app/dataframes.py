import pandas as pd
import numpy as np


class HalfNormal:
    def __init__(self, params, name_of_elasticities = None, epsilon = None) -> None:
        self.name_of_elasticities = name_of_elasticities

        # Basic estimations
        self.sigma_v = params[0]
        self.sigma_u = params[1]
        self.elasticities = params[2:]

        # Compound estimations
        self.intercept = self.elasticities[0]
        self.lamda = self.sigma_u / self.sigma_v
        self.sigma2 = self.sigma_u**2 + self.sigma_v**2
        self.sigma = np.sqrt(self.sigma2)
        self.gamma = self.sigma_u**2 / self.sigma2
        # Gamma is a common paramerization of SFA normal-half normal model,
        # the interpretation is similar to lamda. If gamma =~ 0 then the noise
        # is dominant, and gamma =~ 1 means the inefficience is

        # Jondrow
        self.sigma_star = self.sigma_u*self.sigma_v/self.sigma
        if epsilon:
            self.mu_star = epsilon * self.sigma_u**2/self.sigma2
        else:
            self.mu_star = self.sigma_u**2/self.sigma2 # MISSING MULTIPLYING IT BY EPSILON

        self.epsilon = epsilon
        self.rhs = None

    def dataframe(self, selection="full"):
        df_sfa_estimations = pd.DataFrame(
            {
                "sigma_v": self.sigma_v,
                "sigma_u": self.sigma_u,
                "sigma": self.sigma,
                "lambda": self.lamda,
                "gamma": self.gamma,
            },index=["SFA"]
        )

        elasticities = {"constant": self.intercept}
        if self.name_of_elasticities:
            assert len(self.name_of_elasticities) == len(self.elasticities) - 1 
            for name, param in zip(self.name_of_elasticities, self.elasticities[1:]):
                elasticities[name] = param
        else:
            for i, param in enumerate(self.elasticities[1:]):
                elasticities[f"x{i+1}"] = param

        df_elasticities = pd.DataFrame(elasticities,index=["elasticities"])
        return df_sfa_estimations, df_elasticities

    def add_compund_error(self, data, output_column = 'loutput'):
        if not self.name_of_elasticities:
            raise Exception
        
        self.rhs = self.intercept
        for i, param in enumerate(self.name_of_elasticities):
            self.rhs = self.rhs + data[param] * self.elasticities[i + 1]

        if isinstance(output_column, str):
            self.epsilon = data[output_column] - self.rhs
        else:
            self.epsilon = output_column - self.rhs


    def add_epsilon_to_mu_star(self, epsilon = None):
        """mu_star is multiplied by the estimate of the compund error. If it 
        wasn't given before, do it now
        
        Note that this changes self.mu_star from a float to a numpy array"""

        if epsilon:        
            self.mu_star = epsilon*self.mu_star
        elif self.epsilon is not None:
            self.mu_star = self.epsilon*self.mu_star
        else:
            raise Exception

