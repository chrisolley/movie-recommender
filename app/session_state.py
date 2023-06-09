import streamlit as st
import psycopg2
import time
import hashlib


class SessionState:

    def __init__(self):
        if not SessionState.is_initialized():
            self.initialize()

    @staticmethod
    def initialize():
        st.session_state['user_id'] = ''
        st.session_state['unique_user_id'] = ''
        st.session_state['session_timestamp'] = int(time.time())
        st.session_state['liked_movies'] = list()
        st.session_state['rated_movies'] = list()
        st.session_state['recommender'] = ''
        st.session_state['recommended_movies'] = list()
        st.session_state['n_movies_reviewed'] = 0
        st.session_state['n_movies_to_rate'] = 0
        st.session_state['n_movies_to_review'] = 0
        st.session_state['added_movies_to_review'] = False
        st.session_state['allowed_recommender_movies'] = list()
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
    def get_session_timestamp():
        return st.session_state['session_timestamp']

    @staticmethod
    def set_user_id(user_id):
        st.session_state['user_id'] = user_id
        st.session_state['unique_user_id'] = hashlib.md5(f"{user_id}_{int(time.time())}".encode('UTF-8')).hexdigest()

    @staticmethod
    def has_user_id():
        return len(st.session_state['user_id']) > 0

    @staticmethod
    def title_select_callback():
        st.session_state['title_selection'] = ''

    @staticmethod
    def add_liked_movie(movie_id):
        st.session_state['rated_movies'].append(movie_id)
        st.session_state['liked_movies'].append(movie_id)
        SessionState.save_liked_movie(movie_id)
        SessionState.title_select_callback()

    @staticmethod
    def get_n_liked_movies():
        return len(st.session_state['liked_movies'])

    @staticmethod
    def get_liked_movies():
        return st.session_state['liked_movies']

    @staticmethod
    def add_rated_movie(movie_id):
        st.session_state['rated_movies'].append(movie_id)
        SessionState.title_select_callback()

    @staticmethod
    def get_n_rated_movies():
        return len(st.session_state['rated_movies'])

    @staticmethod
    def set_n_movies_to_rate(n):
        st.session_state['n_movies_to_rate'] = n

    @staticmethod
    def get_n_movies_to_rate():
        return st.session_state['n_movies_to_rate']

    @staticmethod
    def get_rated_movies():
        return st.session_state['rated_movies']

    @staticmethod
    def add_recommended_movies(movies):
        st.session_state['recommended_movies'].extend(movies)
        st.session_state['n_movies_to_review'] += len(movies)

    @staticmethod
    def get_n_reviewed_movies():
        return st.session_state['n_movies_reviewed']

    @staticmethod
    def set_allowed_recommender_movies(movie_ids):
        st.session_state['allowed_recommender_movies'] = movie_ids

    @staticmethod
    def get_allowed_recommender_movies():
        return st.session_state['allowed_recommender_movies']

    @staticmethod
    def get_next_movie_to_review():
        idx = SessionState.get_n_reviewed_movies()
        st.session_state['n_movies_reviewed'] += 1
        return st.session_state['recommended_movies'][idx]

    @staticmethod
    def finished_rating():
        return SessionState.get_n_liked_movies() == st.session_state['n_movies_to_rate']

    @staticmethod
    def finished_adding_constraints():
        return len(SessionState.get_allowed_recommender_movies()) > 0

    @staticmethod
    def finished_adding_movies():
        return st.session_state['added_movies_to_review']

    @staticmethod
    def set_finished_adding_movies():
        st.session_state['added_movies_to_review'] = True

    @staticmethod
    def finished_reviewing():
        return (SessionState.get_n_reviewed_movies() > 0) & \
               (SessionState.get_n_reviewed_movies() == st.session_state['n_movies_to_review'])

    @staticmethod
    def get_session_stage():
        if not SessionState.has_user_id():
            return 'user_entry_stage'
        elif not SessionState.finished_rating():
            return 'movie_rating_stage'
        elif not SessionState.finished_adding_constraints():
            return 'add_constraints_stage'
        elif not SessionState.finished_adding_movies():
            return 'adding_movies_stage'
        elif not SessionState.finished_reviewing():
            return 'movie_review_stage'
        else:
            return 'end_stage'

    @staticmethod
    def execute_query(query):
        with st.session_state['db_conn'].cursor() as cur:
            cur.execute(query)
            st.session_state['db_conn'].commit()

    @staticmethod
    def add_movie_rating(movie_id, recommender, rating, recommender_score):
        SessionState.execute_query(f"""
            INSERT INTO Ratings VALUES(
                '{SessionState.get_unique_user_id()}',
                '{SessionState.get_user_id()}',
                '{recommender}',
                '{movie_id.replace("'", "")}',
                {recommender_score},
                {rating},
                {SessionState.get_session_timestamp()}
            );
        """)

    @staticmethod
    def save_liked_movie(movie_id):
        SessionState.execute_query(f"""
            INSERT INTO Liked VALUES(
                '{SessionState.get_unique_user_id()}',
                '{SessionState.get_user_id()}',
                '{movie_id.replace("'", "")}',
                {SessionState.get_session_timestamp()}
            );
        """)