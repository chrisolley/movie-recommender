import streamlit as st
from session_state import SessionState
from data import Data
from model import Model, BasicModel
from layouts import make_selection_layout, make_recommendation_layout, make_recommender_constraints_layout

N_MOVIES_TO_RATE = 3
N_MOVIES_TO_REVIEW = 5


def app(n_movies_to_rate, n_movies_to_review):
    ss = SessionState(n_movies_to_rate)

    data = Data('../data/movie_summary.csv',
                '../data/movies', ss)

    model_v1 = Model('embeddings_v1',
                     'Recommender 1',
                     '../data/embeddings_v1.npy',
                     '../data/movie_ids.txt')

    model_v2 = Model('embeddings_v2',
                     'Recommender 2',
                     '../data/embeddings_v2.npy',
                     '../data/movie_ids.txt')

    basic_model = BasicModel()

    st.title('Movie Recommender App')

    if ss.get_session_stage() == 'user_entry_stage':
        st.write('This app generates movie recommendations based on a small set of user-input movies. '
                 'It does this via movie description embeddings & user-specified constraints.')

        st.write('The app is currently in the testing phase, so multiple recommendations will be provided and you will '
                 'be asked to rate them.')

        user_id = st.text_input("To get started, please provide a user id!")
        ss.set_user_id(user_id)
        st.button('Submit')

    elif ss.get_session_stage() == 'movie_rating_stage':
        make_selection_layout(data, ss)

    elif ss.get_session_stage() == 'add_constraints_stage':
        make_recommender_constraints_layout(data, ss)

    elif ss.get_session_stage() == 'adding_movies_stage':
        ss.add_recommended_movies(model_v1.get_similar_movies(
            ss.get_liked_movies(), n_movies_to_review, ss.get_rated_movies(), ss.get_allowed_recommender_movies()))
        ss.add_recommended_movies(model_v2.get_similar_movies(
            ss.get_liked_movies(), n_movies_to_review, ss.get_rated_movies(), ss.get_allowed_recommender_movies()))
        ss.add_recommended_movies(basic_model.get_similar_movies(
            data, n_movies_to_review, ss.get_rated_movies(), ss.get_allowed_recommender_movies()))
        ss.set_finished_adding_movies()
        st.experimental_rerun()

    elif ss.get_session_stage() == 'movie_review_stage':
        make_recommendation_layout(data, ss)

    else:
        st.header("Thank you for participating!")
        st.subheader("Feel free to try again with a different movie selection!")


if __name__ == '__main__':
    app(N_MOVIES_TO_RATE, N_MOVIES_TO_REVIEW)
