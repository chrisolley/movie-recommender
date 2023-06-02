CREATE TABLE Ratings(
	unique_user_id VARCHAR(128),
	user_id VARCHAR(128),
	recommender VARCHAR(128),
	movie_id VARCHAR(128),
	recommender_score NUMERIC,
	user_score INTEGER
);

CREATE TABLE Liked(
	unique_user_id VARCHAR(128),
	user_id VARCHAR(128),
	movie_id VARCHAR(128),
);