import streamlit as st
from session_state import SessionState
from data import Data
from model import Model
from layouts import make_selection_layout, make_recommendation_layout

N_MOVIES_TO_RATE = 3
N_MOVIES_TO_REVIEW = 5


def app(n_movies_to_rate, n_movies_to_review):
    ss = SessionState(n_movies_to_rate, n_movies_to_review)

    data = Data('../data/movie_summary.csv',
                '../data/movies',
                ss)

    model = Model('embeddings_v2',
                  '../data/embeddings_v2.npy',
                  '../data/movie_ids.txt')

    st.title('Movie Rating App')

    if not ss.has_user_id():
        user_id = st.text_input("Please enter a user id!")
        ss.set_user_id(user_id)

    if ss.has_user_id() and not ss.finished_rating():
        make_selection_layout(data, ss)

    if ss.has_user_id() and ss.finished_rating() and not ss.finished_reviewing():
        ss.set_recommender_name(model.model_name)
        ss.add_recommended_movies(model.get_similar_movies(ss.get_liked_movies(), n_movies_to_review))
        make_recommendation_layout(data, ss)

    if ss.finished_reviewing():
        st.header("Thank you for participating!")


if __name__ == '__main__':
    app(N_MOVIES_TO_RATE, N_MOVIES_TO_REVIEW)
