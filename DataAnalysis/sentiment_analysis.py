count_vectorizer = CountVectorizer(max_features=1000, min_df=8)
feature_vector = count_vectorizer.fit(df["lemmatized_text"])
# To get a list of all unique words
features = feature_vector.get_feature_names()
# To get a sparse matrix of the words in the text
df_features = count_vectorizer.transform(df["lemmatized_text"])