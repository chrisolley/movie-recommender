import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy.fuzz import token_set_ratio


class Model:
    def __init__(self, model_name, public_model_name, embeddings_path, embeddings_movie_ids_path, data):
        self.model_name = model_name
        self.public_model_name = public_model_name
        self.embeddings = Model.load_embeddings(embeddings_path)
        self.embeddings_movie_ids = Model.load_ids(embeddings_movie_ids_path)
        self.embeddings_movie_ids_reverse = Model.load_ids_reversed(embeddings_movie_ids_path)
        self.data = data

    @staticmethod
    @st.cache_data
    def load_embeddings(file_path):
        with open(file_path, 'rb') as fp:
            embeddings = np.load(fp)
        return embeddings

    @staticmethod
    @st.cache_data
    def load_ids(file_path):
        with open(file_path, 'r') as fp:
            movie_ids = {movie: idx for idx, movie in enumerate(fp.read().split(', '))}
        return movie_ids

    @staticmethod
    @st.cache_data
    def load_ids_reversed(file_path):
        with open(file_path, 'r') as fp:
            movie_ids = {idx: movie for idx, movie in enumerate(fp.read().split(', '))}
        return movie_ids

    # @st.cache_data
    def get_similar_movies(self, selected_movies, n, filtered_movies=None, included_movies=None):
        user_embedding = []
        filtered_movie_ids, included_movie_ids = [], []
        selected_movie_ids = [self.embeddings_movie_ids[movie] for movie in selected_movies]
        if filtered_movies:
            filtered_movie_ids = [self.embeddings_movie_ids[movie] for movie in filtered_movies]
        if included_movies:
            included_movie_ids = [self.embeddings_movie_ids[movie] for movie in included_movies]

        for movie_id in selected_movie_ids:
            user_embedding.append(self.embeddings[movie_id])
        user_embedding = np.mean(np.array(user_embedding), axis=0).reshape(1, -1)

        return self.get_similar_movies_from_user_embedding(user_embedding, n, selected_movies,
                                                           filtered_movie_ids, included_movie_ids)

    def get_similar_movies_from_user_embedding(self, user_embedding, n, selected_movies, filtered_movie_ids,
                                               included_movie_ids):
        similarity_matrix = cosine_similarity(self.embeddings, user_embedding)
        similarities = sorted([(i, similarity[0]) for i, similarity in
                               enumerate(similarity_matrix)], key=lambda x: x[1], reverse=True)
        similar_movies = list()
        selected_movie_titles = [self.data.get_movie(selected_movie)['title'] for selected_movie in selected_movies]
        for idx, similarity in similarities:
            movie = self.data.get_movie(self.embeddings_movie_ids_reverse[idx])
            max_similarity = max([token_set_ratio(movie['title'], title) for title in selected_movie_titles])
            if len(similar_movies) == n:
                break
            if (idx in filtered_movie_ids) or (idx not in included_movie_ids) or (max_similarity > 65):
                continue
            similar_movies.append((self.embeddings_movie_ids_reverse[idx], similarity, self.model_name,
                                   self.public_model_name))
        return similar_movies


class BasicModel:
    def __init__(self):
        self.model_name = 'rating_model'
        self.public_model_name = 'Recommender 3'

    def get_similar_movies(self, data, n, filtered_movies=None, included_movies=None):
        similar_movies = list()
        for _, movie in data.movies.sort_values('rating', ascending=False).iterrows():
            if len(similar_movies) == n:
                break
            if (movie['movie_id'] in filtered_movies) or (movie['movie_id'] not in included_movies):
                continue
            similar_movies.append((movie['movie_id'], 0.5, self.model_name, self.public_model_name))
        return similar_movies
