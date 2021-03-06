# -*- coding: utf-8 -*-
"""HCV.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dYWqr38TPtDQueOFd3jNnY3sxG1GDTAw

# HCV Data Analysis
"""

from google.colab import drive
drive.mount("gdrive")

"""## Import necessary libraries"""

#utils and plot libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import graphviz
import seaborn as sns

#machine learn libraries
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import tensorflow as tf

"""## Read the dataset"""

df = pd.read_csv("/content/gdrive/My Drive/DataAnalysis/HCV/hcvdat0.csv")

df.head()

"""## Meta analysis regarding to the dataset"""

df.describe()

"""All attributes except Category and Sex are numerical. The laboratory data are the attributes 5-14.
1. X (Patient ID/No.)
2. Category (diagnosis) (values: '0=Blood Donor', '0s=suspect Blood Donor', '1=Hepatitis', '2=Fibrosis', '3=Cirrhosis')
3. Age (in years)
4. Sex (f,m)
5. ALB
6. ALP
7. ALT
8. AST
9. BIL
10. CHE
11. CHOL
12. CREA
13. GGT
14. PROT
"""

df.info()

"""It can be observed that there are NaN values existing in our dataset which needs to be handled.

## Data Cleansing
"""

for col in df.columns:
  print(col,"contains:",df[col].isnull().sum())

df.Category.unique()

category_dict = {
    '0=Blood Donor':0, '0s=suspect Blood Donor':1, '1=Hepatitis':2,
       '2=Fibrosis':3, '3=Cirrhosis':4
}
df.Category = df.Category.map(category_dict)
sex_dict = {
    'm':0,
    'f':1
}
df.Sex = df.Sex.map(sex_dict)
imputer = KNNImputer(n_neighbors=3)
new = pd.DataFrame(data=imputer.fit_transform(df),columns=df.columns)

new.head(-1)

for col in new.columns:
  print(col,"contains:",new[col].isnull().sum())

"""Dataset is clean now.

## EDA

First thing to check regarding on the dataset is the balance.
"""

new.Category.value_counts()

"""The classes are exteremely unbalanced and due to the the number of instances is low this condition will cause almost any model to work wrong."""

category_dict

"""What we are trying to do is actually manage to identify whether a patient has hepatitis or not.We can manipulate data in a manner that can show a better performance or our models will show great accuracy but very low ability to identify HCV."""

category_dict = {
  0:0,
  1:0,
  2:1,
 3:1,
 4:1
}

new["Category"] = new["Category"].map(category_dict)

"""We have changed the task of classification from multi-class to binary and resulted our models to have enough performance now lets check if we can increase it more."""

sns.heatmap(new.drop(columns=["Unnamed: 0"]).corr())

"""Some enzymes and proteins shows correlation between but this is an expected situation , we will try to dig deeper in order to find any relation which can help us in model training."""

sns.pairplot(data=new)

"""EDA was a cheap shot in this analysis since most of the data in here contains natural correlation in between which is not a pattern to follow deeply.

## Data Preprocessing

* Scaling
* One-Hot Encoding

Before starting to get into the real pre-processing lets eliminate the Unnmaed:0 field since it is useless.
"""

new = new.drop(columns=["Unnamed: 0"])
new.head()

"""Before starting to normalize , lets extract categorical fields since it is not the best practice to normalize them too."""

cat_fields = new[["Category","Sex"]]
non_cat_fields = new.drop(columns=["Category","Sex"])

"""Standard scaler showed better performance compared to MinMax scaler which is why it is used."""

# fit scaler on training data
norm = StandardScaler().fit_transform(non_cat_fields)

non_cat_fields = pd.DataFrame(norm,columns=non_cat_fields.columns)

"""One-Hot Encoding before concatenating the categorical data with continious data."""

cat_fields = pd.get_dummies(cat_fields)
for col in cat_fields.columns:
  non_cat_fields[col] = cat_fields[col]

counter=0
for index, row in non_cat_fields.iterrows():
    if row['Category'] == 0 and counter<100:
        non_cat_fields.drop(index, inplace=True)
        counter+=1

"""Train Test Data Split with Test Size 0.33 and Random State = 42"""

X_train,X_test,y_train,y_test = train_test_split(non_cat_fields.drop(columns=["Category"]),non_cat_fields["Category"],test_size=0.33,random_state=42)

"""In order to compare a default classifier is used without even making any CV."""

clf = DecisionTreeClassifier()
clf.fit(X_train,y_train)
clf.score(X_test,y_test)

"""Model has a high accuracy score but since the dataset is unbalanced,we can not trust accuracy score,other performance metrics needs to be considered."""

from sklearn.metrics import classification_report
print(classification_report(clf.predict(X_test),y_test))

from IPython.display import Image
import pydot
import pydotplus

out_file = tree.export_graphviz(
    clf,
    feature_names   = X_train.columns,
    filled          = True,
    rounded         = True
)
graph = pydotplus.graph_from_dot_data(out_file)
Image(graph.create_png())

"""## ANN for binary classification"""

model = tf.keras.Sequential()

model.add(tf.keras.layers.Flatten(input_shape=(12,)))

model.add(tf.keras.layers.Dense(16, activation='swish'))

model.add(tf.keras.layers.Dense(16, activation='swish'))

model.add(tf.keras.layers.Dense(16, activation='swish'))

model.add(tf.keras.layers.Dense(16, activation='swish'))

model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

model.compile(loss="binary_crossentropy",optimizer="adam",metrics=['accuracy'])

model.fit(X_train,y_train,epochs=30,batch_size=1)

print(classification_report(model.predict_classes(X_test),y_test))