import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import contextily
import numpy as np

#import income data from csv
#Note this is not avg household income but its pretty close. This is total income/total respondents 
fsa = pd.read_csv('FSA.csv').sort_values(by=['Avg Income'])
#print(fsa)

#import yelp api
api_key = "y33jHkcCZGE6lzQYWLbpn0BQjwrn889ju7-2GPaYW6vG4R6fTlqFYSw8F-rVlF9ZbCBAeNiRe6pjRI019VlgAHJ6e7wHW_0ScuPyl3fOrX2z7EP8-qX7HWxer8-NX3Yx" #  Replace this with your real API key
headers = {'Authorization': 'Bearer %s' % api_key}
url='https://api.yelp.com/v3/businesses/search'


data = []
for offset in range(0, 1000, 50):
        params = {
            'limit': 50, 
            'location': 'Vancouver',
            #'radius': 40000,
            'offset': offset
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data += response.json()['businesses']
        elif response.status_code == 400:
            print('400 Bad Request')
            break
df_van = pd.DataFrame(data)

data = []
for offset in range(0, 1000, 50):
        params = {
            'limit': 50, 
            'location': 'Richmond, BC',
            #'radius': 40000,
            'offset': offset
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data += response.json()['businesses']
        elif response.status_code == 400:
            print('400 Bad Request')
            break
df_rich = pd.DataFrame(data)

data = []
for offset in range(0, 1000, 50):
        params = {
            'limit': 50, 
            'location': 'Surrey, BC',
            #'radius': 40000,
            'offset': offset
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data += response.json()['businesses']
        elif response.status_code == 400:
            print('400 Bad Request')
            break
df_surr = pd.DataFrame(data)
df = pd.concat([df_van, df_rich, df_surr])
print(df)

#Index(['id', 'alias', 'name', 'image_url', 'is_closed', 'url', 'review_count',
       #'categories', 'rating', 'coordinates', 'transactions', 'price',
       #'location', 'phone', 'display_phone', 'distance']

#create df
df2 = pd.concat([df["location"].apply(pd.Series), df["categories"].apply(pd.Series), df["coordinates"].apply(pd.Series), df[["name", "price", "rating", "review_count", "distance", "is_closed"]]], axis = 1)
print(df2)
df3 = pd.concat([df2[0].apply(pd.Series), df2[["name", "latitude", "longitude", "zip_code", "price", "rating", "review_count", "distance", "is_closed"]]], axis = 1).dropna()
print(df3)
print(df3['title'].nunique())
df3["leftzip"] = df3['zip_code'].str[:3]
df3["price_updated"]= df3["price"].replace('$', 1).replace('$$', 2).replace('$$$', 3).replace('$$$$', 4)

df3 = pd.merge(df3, fsa, left_on='leftzip', right_on='Country', how='left')
print(df3.describe())
#percentile 
#percentile = (df3.quantile([.33, .67], axis = 0))

df3["level"] = np.where(df3["Avg Income"] < 45000, 1, np.where(df3["Avg Income"] > 65000, 3, 2))
df3 = df3[df3.is_closed == False]
df3 = df3[df3.review_count >= 50]
df3["count"] = 1 #helper column
print(df3[["name", "leftzip", "price_updated", "rating", "title", "Electoral District", "Avg Income", "level", "count", "review_count", "distance", "is_closed"]])
#print(df3[["name", "leftzip", "price_updated", "rating", "title", "Electoral District", "Avg Income"]].loc[df3["rating"] == 2.5])
#print(df3['Code'].isnull().values.any())

#createmap
fig, ax = plt.subplots()
ax.plot(df3['longitude'], df3['latitude'], 'o', markersize=2, alpha=0.5)
contextily.add_basemap(ax, source=contextily.providers.CartoDB.Voyager, crs='EPSG:4326')
plt.show()

corrMatrix = df3[["rating", "price_updated", "distance", "review_count", "Avg Income"]].corr()
sns.heatmap(corrMatrix, annot=True)
plt.show()

ax = sns.countplot(x="Electoral District", data=df3)
plt.title("restaurant count per district")
plt.xticks(
    rotation=45, 
    horizontalalignment='right')
plt.show()


#create charts
ax = sns.countplot(x="rating", data=df3)
plt.title("restaurant count per rating")
plt.show()

#ax = sns.countplot(x="price_updated", data=df3, order=["1", "2", "3", "4"])
#plt.title("restaurant count per price range")
#plt.show()

#ax = sns.countplot(x="title", data=df3)
#plt.xticks(
    #rotation=45, 
    #horizontalalignment='right')
#plt.title("restaurant count per category")
#plt.show()

ax = sns.violinplot(x="rating", y="price_updated", data=df3)
plt.xlabel('avg rating')
plt.ylabel('avg price')
plt.title("avg price per rating")
plt.show()

ax = sns.violinplot(x="rating", y="distance", data=df3)
plt.xlabel('avg rating')
plt.ylabel('avg distance')
plt.title("avg distance on rating")
plt.show()
plt.show()

ax = sns.violinplot(x="rating", y="Avg Income", data=df3)
plt.xlabel('avg rating')
plt.ylabel('avg income')
plt.title("avg income per rating")
plt.show()

#ax = df3.pivot_table(values="count", index="price_updated", columns="level", aggfunc=np.sum).plot(kind="bar")
#plt.title("restaurant distribution by price")
#plt.show()












from sklearn.svm import LinearSVC
from sklearn.datasets import load_iris
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from mlxtend.plotting import plot_decision_regions

#find means

df_low = df3[df3.level == 1]
df_low = df_low["rating"]
mean_low = df_low.mean()

df_high = df3[df3.level == 3]
df_high = df_high["rating"]
mean_high = df_high.mean()
'''
'''

#create helper columns
df3["low_check"] = np.where(df3["rating"] >= 4, 1, 0)
df3["high_check"] = np.where(df3["rating"] >= 4, 1, 0)

df3 = df3[["price_updated", "review_count", "low_check", "high_check", "level", "distance"]]
df4 = df3[df3.level == 1]
df4 = df4[["review_count", "price_updated", "low_check"]]
print(df4)
print(df4.describe())

df5 = df3[df3.level == 3]
df5 = df5[["review_count", "price_updated", "high_check"]]
print(df5)
print(df5.describe())

#train in low
X_low = df4.drop('low_check', axis=1).to_numpy()
y_low = df4['low_check'].to_numpy()
X_high = df5.drop('high_check', axis=1).to_numpy()
y_high = df5['high_check'].to_numpy()

X_train = X_low
X_test = X_high
y_train = y_low
y_test = y_high

# Training a classifier
from sklearn.svm import SVC
svclassifier = SVC(kernel='linear')
svclassifier.fit(X_train, y_train)

y_pred = svclassifier.predict(X_test)

#results
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
plot_decision_regions(X_train, y_train, clf=svclassifier, legend=2)
plt.xlabel('review_count')
plt.ylabel('price')
plt.title('SVM - high income restaurants in low income model')
plt.show() 


#train in high
X_train = X_high
X_test = X_low
y_train = y_high
y_test = y_low

# Training a classifier
from sklearn.svm import SVC
svclassifier = SVC(kernel='linear')
svclassifier.fit(X_train, y_train)

y_pred = svclassifier.predict(X_test)

#results
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
plot_decision_regions(X_train, y_train, clf=svclassifier, legend=2)
plt.xlabel('price')
plt.ylabel('review_count')
plt.title('SVM - low income restaurants in high income model')
plt.show()

