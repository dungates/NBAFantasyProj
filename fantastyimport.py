import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas import plotting
from scipy import stats
import os
import warnings

warnings.filterwarnings("ignore")
from scipy import stats

sns.set(rc={"figure.figsize": (11.7, 8.27)})
sns.set_context("poster")


from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, confusion_matrix, classification_report
from sklearn.gaussian_process import GaussianProcessClassifier

plt.style.use("ggplot")
sns.set(style="whitegrid", color_codes=True, rc={"figure.figsize": (12, 12)})

for dirname, _, filenames in os.walk("/kaggle/input"):
    for filename in filenames:
        print(os.path.join(dirname, filename))
