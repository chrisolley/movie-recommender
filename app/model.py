import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Model:
    def __init__(self, model_name, embeddings_path, embeddings_movie_ids_path):
        self.model_name = model_name
        self.embeddings = Model.load_embeddings(embeddings_path)
        self.embeddings_movie_ids = Model.load_ids(embeddings_movie_ids_path)
        self.embeddings_movie_ids_reverse = Model.load_ids_reversed(embeddings_movie_ids_path)

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
    def get_similar_movies(self, selected_movies, n):
        user_embedding = []
        selected_movie_ids = [self.embeddings_movie_ids[movie] for movie in selected_movies]

        for movie_id in selected_movie_ids:
            user_embedding.append(self.embeddings[movie_id])

        user_embedding = np.mean(np.array(user_embedding), axis=0)
        similarity_matrix = cosine_similarity(self.embeddings, user_embedding.reshape(1, -1))

        return [(self.embeddings_movie_ids_reverse[movie], score) for movie, score in
                self.get_similar_movies_from_matrix(similarity_matrix, n, selected_movie_ids)]

    @staticmethod
    def get_similar_movies_from_matrix(similarity_matrix, n, movie_ids_to_filter):
        similarities = sorted([(i, similarity[0]) for i, similarity in
                               enumerate(similarity_matrix)], key=lambda x: x[1], reverse=True)
        similar_movies = list()
        for idx, similarity in similarities:
            if len(similar_movies) == n:
                break
            if idx in movie_ids_to_filter:
                continue
            similar_movies.append((idx, similarity))
        return similar_movies
