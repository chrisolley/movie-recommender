import pandas as pd
import streamlit as st
import random
import itertools
from PIL import Image


class Data:
    def __init__(self, metadata_path, image_path, session_state):
        self.movies = Data.load_data(metadata_path)
        if not session_state.is_data_initialized():
            self.filtered_movies = self.movies
        self.image_path = image_path

    @staticmethod
    @st.cache_data
    def load_data(file_path):
        return pd.read_csv(file_path)

    def get_movie(self, movie_id):
        return self.movies[self.movies['movie_id'] == movie_id].iloc[0].to_dict()

    def get_random_movie(self):
        return self.filtered_movies.iloc[int(random.random() * self.filtered_movies.shape[0])].to_dict()

    def filter_movies(self, year_start, year_end, genres, directors, starring, title, excluded_movies):
        self.filtered_movies = self.movies[
            (self.movies['release_year'] >= year_start) &
            (self.movies['release_year'] <= year_end) &
            (len(genres) == 0 or self.movies['genres'].str.contains("|".join(genres))) &
            (len(directors) == 0 or self.movies['director'].str.contains("|".join(directors))) &
            (len(starring) == 0 or self.movies['starring'].str.contains("|".join(starring))) &
            (len(title) == 0 or self.movies['title'] == title) &
            (~self.movies['movie_id'].isin(excluded_movies))
        ]

    def get_n_filtered_movies(self):
        return len(self.filtered_movies)

    def get_all_titles(self):
        titles = sorted(list(self.filtered_movies['title']))
        titles.insert(0, '')
        return titles

    def get_all_genres(self):
        genres = list(self.filtered_movies['genres'].apply(lambda x: [g.strip() for g in x.split(',')]))
        return set(itertools.chain.from_iterable(genres))

    def get_all_directors(self):
        return set(list(self.filtered_movies['director']))

    def get_all_actors(self):
        actors = list(self.filtered_movies['starring'].apply(lambda x: [g.strip() for g in x.split(',')]))
        return set(itertools.chain.from_iterable(actors))

    def get_all_years(self):
        return list(self.movies['release_year'])

    def get_movie_poster(self, movie_id):
        return Image.open(f"{self.image_path}/{movie_id}/poster.png")
