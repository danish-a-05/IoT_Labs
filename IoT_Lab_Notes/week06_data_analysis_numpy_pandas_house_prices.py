# =============================================================================
#  WEEK 6 - DATA ANALYSIS WITH NUMPY, PANDAS AND MATPLOTLIB
#  Week 6 lecture + Lab 6.   Runs on: LAPTOP
#     pip install numpy pandas matplotlib
#  Put daft_ie_v1.csv (from the Brightspace zip) in the same folder.
# =============================================================================
#  LECTURE NOTES
#  * Types of analysis: DESCRIPTIVE (what happened), PREDICTIVE (what will
#    happen), PRESCRIPTIVE (what should we do).
#  * Four Vs of big data: Volume (amount), Velocity (how often),
#    Variety (how unpredictable), Veracity (how accurate).
#  * States of data: in MOTION (on the network), at REST (on disk),
#    in USE (being processed).
#  * Stats words: mean, median, mode, standard deviation, percentiles.
#  * Dimensionality reduction: shrink many columns into a few
#    (PCA, LDA, autoencoders).
#  * Pearson correlation: from -1 to +1. How well one variable predicts
#    another. +1 = rise together, 0 = no link, -1 = opposite.
# =============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- NUMPY ----
a = np.array([[1, 2, 3],
              [4, 5, 6]])
print(a.ndim, a.shape, a.size, a.dtype)   # 2  (2, 3)  6  int64

print(np.zeros((3, 3)))                   # 3x3 of zeros
print(np.ones((3, 3)))                    # 3x3 of ones
print(np.arange(0, 10, 2))                # [0 2 4 6 8]   (10 not included)
print(np.linspace(0, 10, 12))             # 12 numbers from 0 to 10 (included)
print(np.linspace(0, 10, 12).reshape(4, 3))

x = np.array([[1, 2], [3, 4]])
y = np.array([[5, 6], [7, 8]])
print(x * y)                              # multiply each element
print(x @ y)                              # matrix multiplication
print(a[0, 1], a[:, 2], a[::-1])          # indexing: [row, column]
print(a.ravel(), np.vstack([x, y]), np.hstack([x, y]))

# --------------------------------------------------------------- PANDAS ----
students = pd.DataFrame({
    'Name': ['John', 'Mary', 'Bob', 'Anne'],
    'Average exam result': [70, 80, 65, 85],
})
print(students['Name'])                                 # one column
print(students.loc[0])                                  # one row
print(students[students['Average exam result'] >= 80])  # filter, like SQL

# ---------------------------------------------------------------- LAB 6 ----
data = pd.read_csv('daft_ie_v1.csv', header=0, index_col=0)

print(data.columns)
print(data.head())
print('Most expensive house:', data['price'].max())
print(data[['price', 'numBedrooms', 'numBathrooms']].describe())

# Scatter plot: price vs bedrooms
fig, ax = plt.subplots()
ax.scatter(data['numBedrooms'], data['price'])
ax.set_xlabel('Number of bedrooms')
ax.set_ylabel('Price')
plt.show()
# Try the same with 'numBathrooms', 'propertySize' and 'publishDate'.

# Bar chart: average price per property type
average_by_type = data.groupby('propertyType')['price'].mean()
fig, ax = plt.subplots()
ax.bar(average_by_type.index, average_by_type.values)
ax.set_ylabel('Average price')
plt.xticks(rotation=45)
plt.show()

# Bar chart: average price per county.
# The county is the last part of the title, e.g. "..., Co. Cork"
data['county'] = data['title'].str.split(',').str[-1]
average_by_county = data.groupby('county')['price'].mean()
fig, ax = plt.subplots()
ax.bar(average_by_county.index, average_by_county.values)
plt.xticks(rotation=90)
plt.show()

# Correlation. numeric_only=True is needed in new versions of pandas,
# otherwise it errors on the text columns.
correlation = data.corr(numeric_only=True).round(decimals=2)
print(correlation['price'])
print('Price vs bedrooms:', correlation['price']['numBedrooms'])

# Heatmap of the correlations
names = list(correlation.columns)
corr = correlation.to_numpy()
fig, ax = plt.subplots()
ax.imshow(corr)
ax.set_xticks(range(len(names)), labels=names, rotation=90)
ax.set_yticks(range(len(names)), labels=names)
for i in range(len(names)):
    for j in range(len(names)):
        ax.text(j, i, corr[i, j], ha='center', va='center', fontsize=6)
plt.show()
