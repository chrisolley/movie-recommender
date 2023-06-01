import streamlit as st


def make_selection_layout(data, session_state):
    st.header("Instructions")
    st.markdown(
        f'**Please select {session_state.get_n_movies_to_rate()} movies '
        f'in order to generate recommendations. '
        f'({session_state.get_n_liked_movies()} / {session_state.get_n_movies_to_rate()})**')

    st.header("Filters")
    selected_year_start, selected_year_end = st.slider(
        'Release Year Range',
        int(min(data.get_all_years())),
        int(min(data.get_all_years())),
        (1970, 2023))

    min_rating = st.slider('Minimum Rating', 0.0, 10.0, 6.0, 0.1)

    selected_title = st.selectbox('Title', data.get_all_titles())
    with st.container():
        cols = st.columns(3)
        with cols[0]:
            selected_genres = st.multiselect('Genres', data.get_all_genres(), [])
        with cols[1]:
            selected_directors = st.multiselect('Directors', data.get_all_directors(), [])
        with cols[2]:
            selected_actors = st.multiselect('Starring', data.get_all_actors(), [])

    data.filter_movies(selected_year_start, selected_year_end, min_rating, selected_genres,
                       selected_directors, selected_actors, selected_title, session_state.get_rated_movies())

    if data.get_n_filtered_movies() == 0:
        st.text("No movie matching these filters!")
    else:
        movie = data.get_random_movie()
        try:
            movie_poster = data.get_movie_poster(movie['movie_id'])
        except FileNotFoundError:
            movie_poster = None

        st.header(f"Current Selection")
        st.subheader(movie['title'])

        # movie metadata section
        cols = st.columns([1, 2], gap='small')
        with cols[0]:
            st.markdown(f"**Release Year**: {movie['release_year']}")
            st.markdown(f"**Director**: {movie['director']}")
        with cols[1]:
            st.markdown(f"**Genres**: {movie['genres']}")
            st.markdown(f"**Starring**: {movie['starring']}")

        # movie poster section
        cols = st.columns([1, 3, 1], gap='small')
        with cols[1]:
            if movie_poster:
                st.image(movie_poster)
            else:
                st.write("No movie poster found")
        st.write(movie['plot'])
        # rating section
        cols = st.columns(2, gap='small')
        with cols[0]:
            st.button(":green[Pick this movie!] :+1:",
                      on_click=session_state.add_liked_movie,
                      args=(movie['movie_id'],),
                      use_container_width=True)
        with cols[1]:
            st.button("Show me another movie. :recycle:",
                      on_click=session_state.add_rated_movie, args=(movie['movie_id'],),
                      use_container_width=True)


def make_recommender_constraints_layout(data, session_state):
    def _submit_constraints(_year_start, _year_end, _min_rating, _genres):
        data.filter_movies(_year_start, _year_end, _min_rating, _genres)
        session_state.set_allowed_recommender_movies(data.get_filtered_movies())

    st.header("Recommendations")
    st.write("Apply additional constraints to the movie recommendations.")
    selected_year_start, selected_year_end = st.slider(
        'Release Year Range',
        int(min(data.get_all_years())),
        int(min(data.get_all_years())),
        (1970, 2023), key='rec_constraint_years')
    min_rating = st.slider('Minimum Rating', 0.0, 10.0, 6.0, 0.1, key='rec_constraint_ratings')
    selected_genres = st.multiselect('Genres', data.get_all_genres(), [], key='rec_constraint_genres')
    st.button("Submit",
              on_click=_submit_constraints,
              args=(selected_year_start, selected_year_end, min_rating, selected_genres))


def make_recommendation_layout(data, session_state):
    movie_id, score, model_name, public_model_name = session_state.get_next_movie_to_review()
    movie = data.get_movie(movie_id)
    movie_poster = data.get_movie_poster(movie['movie_id'])

    st.header("Recommendations")
    st.subheader(f"Model: {public_model_name}")
    st.subheader(movie['title'])

    # movie metadata section
    cols = st.columns([1, 2], gap='small')
    with cols[0]:
        st.markdown(f"**Release Year**: {movie['release_year']}")
        st.markdown(f"**Director**: {movie['director']}")

    cols = st.columns([1, 3, 1], gap='small')
    with cols[1]:
        st.image(movie_poster)
    st.write(movie['plot'])
    with cols[1]:
        st.markdown(f"**Genres**: {movie['genres']}")
        st.markdown(f"**Starring**: {movie['starring']}")
    cols = st.columns(5, gap='small')
    with cols[0]:
        st.button(":green[Sweet!] :100:",
                  use_container_width=True,
                  on_click=session_state.add_movie_rating,
                  args=(movie['movie_id'], model_name, 2, score))
    with cols[1]:
        st.button(":green[Not bad!] :+1:",
                  use_container_width=True,
                  on_click=session_state.add_movie_rating,
                  args=(movie['movie_id'], model_name, 1, score))
    with cols[2]:
        st.button("Meh :neutral_face:",
                  use_container_width=True,
                  on_click=session_state.add_movie_rating,
                  args=(movie['movie_id'], model_name, 0, score))
    with cols[3]:
        st.button(":orange[Not good.] :-1:",
                  use_container_width=True,
                  on_click=session_state.add_movie_rating,
                  args=(movie['movie_id'], model_name, -1, score))
    with cols[4]:
        st.button(":red[This sucks!] :face_vomiting:",
                  use_container_width=True,
                  on_click=session_state.add_movie_rating,
                  args=(movie['movie_id'], model_name, -2, score))
