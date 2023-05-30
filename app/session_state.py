import streamlit as st
import psycopg2
import time
import hashlib


class SessionState:

    def __init__(self, n_movies_to_rate, n_movies_to_review):
        if not SessionState.is_initialized():
            self.initialize(n_movies_to_rate, n_movies_to_review)

    @staticmethod
    def initialize(n_movies_to_rate, n_movies_to_review):
        st.session_state['user_id'] = ''
        st.session_state['unique_user_id'] = ''
        st.session_state['liked_movies'] = list()
        st.session_state['rated_movies'] = list()
        st.session_state['recommender'] = ''
        st.session_state['recommended_movies'] = list()
        st.session_state['n_movies_reviewed'] = 0
        st.session_state['n_movies_to_rate'] = n_movies_to_rate
        st.session_state['n_movies_to_review'] = n_movies_to_review
        st.session_state['initialized'] = True
        st.session_state['data_initialized'] = False
        st.session_state['db_conn'] = psycopg2.connect(**st.secrets['postgres'])

    @staticmethod
    def is_initialized():
        return 'initialized' in st.session_state

    @staticmethod
    def is_data_initialized():
        return st.session_state['data_initialized']

    @staticmethod
    def get_user_id():
        return st.session_state['user_id']

    @staticmethod
    def get_unique_user_id():
        return st.session_state['unique_user_id']

    @staticmethod
    def set_user_id(user_id):
        st.session_state['user_id'] = user_id
        st.session_state['unique_user_id'] = hashlib.md5(f"{user_id}_{int(time.time())}".encode('UTF-8')).hexdigest()

    @staticmethod
    def has_user_id():
        return len(st.session_state['user_id']) > 0

    @staticmethod
    def add_liked_movie(movie_id):
        st.session_state['rated_movies'].append(movie_id)
        st.session_state['liked_movies'].append(movie_id)

    @staticmethod
    def get_n_liked_movies():
        return len(st.session_state['liked_movies'])

    @staticmethod
    def get_liked_movies():
        return st.session_state['liked_movies']

    @staticmethod
    def add_rated_movie(movie_id):
        st.session_state['rated_movies'].append(movie_id)

    @staticmethod
    def get_n_rated_movies():
        return len(st.session_state['rated_movies'])

    @staticmethod
    def get_n_movies_to_rate():
        return st.session_state['n_movies_to_rate']

    @staticmethod
    def get_rated_movies():
        return st.session_state['rated_movies']

    @staticmethod
    def set_recommender_name(name):
        st.session_state['recommender'] = name

    @staticmethod
    def get_recommender_name():
        return st.session_state['recommender']

    @staticmethod
    def add_recommended_movies(movies):
        st.session_state['recommended_movies'] = movies

    @staticmethod
    def get_n_reviewed_movies():
        return st.session_state['n_movies_reviewed']

    @staticmethod
    def get_next_movie_to_review():
        idx = SessionState.get_n_reviewed_movies()
        st.session_state['n_movies_reviewed'] += 1
        return st.session_state['recommended_movies'][idx]

    @staticmethod
    def finished_rating():
        return SessionState.get_n_rated_movies() == st.session_state['n_movies_to_rate']

    @staticmethod
    def finished_reviewing():
        return SessionState.get_n_reviewed_movies() == st.session_state['n_movies_to_review']

    @staticmethod
    def execute_query(query):
        with st.session_state['db_conn'].cursor() as cur:
            cur.execute(query)
            st.session_state['db_conn'].commit()

    @staticmethod
    def add_movie_rating(movie_id, rating, recommender_score):
        SessionState.execute_query(f"""
            INSERT INTO Ratings VALUES(
                '{SessionState.get_unique_user_id()}',
                '{SessionState.get_user_id()}',
                '{SessionState.get_recommender_name()}',
                '{movie_id}',
                {recommender_score},
                {rating}
            );
        """)
