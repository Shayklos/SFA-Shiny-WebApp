import pandas as pd
import numpy as np


class HalfNormal:
    def __init__(self, params, name_of_elasticities=None) -> None:
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

