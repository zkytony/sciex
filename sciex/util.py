from scipy import stats
import numpy as np

# Printing
def json_safe(obj):
    if isinstance(obj, bool):
        return str(obj).lower()
    elif isinstance(obj, (list, tuple)):
        return [json_safe(item) for item in obj]
    elif isinstance(obj, dict):
        return {json_safe(key):json_safe(value) for key, value in obj.items()}
    else:
        return str(obj)
    return obj

# Pandas utils
def flatten_column_names(df):
    """Flatten multi-index columns"""
    df.columns = list(map("-".join, df.columns.values))
    df.reset_index(inplace=True)


# computing statistic
def ci_normal(series, confidence_interval=None, c=0.95):
    ### CODE BY CLEMENT at LIS ###
    """Confidence interval for normal distribution with
    unknown mean and variance. `confidence_interval` and `c`
    are the same parameter.
    """
    if confidence_interval is None:
        confidence_interval = c
        
    series = np.asarray(series)
    # this is the "percentage point function" which is the inverse of a cdf
    # divide by 2 because we are making a two-tailed claim
    tscore = stats.t.ppf((1 + confidence_interval)/2.0, df=len(series)-1)
    y_error = stats.sem(series)
    half_width = y_error * tscore
    return half_width

def stderr(series):
    """computes the standard error of the mean"""
    return stats.sem(series)
    
