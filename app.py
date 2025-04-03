import streamlit as st
import pandas as pd
import requests
import pickle

# Load the processed data and similarity matrix
with open('movie_data.pkl', 'rb') as file:
    movies, cosine_sim = pickle.load(file)

# Function to get movie recommendations with percentages
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies
    
    # Extract movie indices and similarity scores
    movie_indices = [i[0] for i in sim_scores]
    similarity_percentages = [round(i[1] * 100, 1) for i in sim_scores]  # Convert to percentage
    
    # Create a DataFrame with titles, IDs, and match percentages
    result_df = movies[['title', 'movie_id']].iloc[movie_indices].copy()
    result_df['match_percentage'] = similarity_percentages
    
    return result_df

# Fetch movie poster from TMDB API
def fetch_poster(movie_id):
    try:
        api_key = '3f8f499f24d9002e1a5a824582abc385'  # Replace with your TMDB API key
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
    return None

# Function to color code the percentage
def get_match_color(percentage):
    if percentage >= 80:
        return "green"
    elif percentage >= 60:
        return "orange"
    else:
        return "red"

# Streamlit UI
st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    with st.spinner('Finding similar movies...'):
        recommendations = get_recommendations(selected_movie)
        st.write(f"### Top 10 Movies Similar to '{selected_movie}'")
        
        # Display the selected movie first
        original_idx = movies[movies['title'] == selected_movie].index[0]
        original_movie_id = movies.iloc[original_idx]['movie_id']
        original_poster = fetch_poster(original_movie_id)
        
        st.write("### Your Selected Movie:")
        if original_poster:
            st.image(original_poster, width=150)
        st.write(f"**{selected_movie}**")
        st.write("---")
        
        st.write("### Recommendations:")
        # Create a 2x5 grid layout
        for i in range(0, 10, 2):  # Loop over rows (5 rows, 2 movies each)
            cols = st.columns(2)  # Create 2 columns for each row
            for col, j in zip(cols, range(i, i+2)):
                if j < len(recommendations):
                    movie_title = recommendations.iloc[j]['title']
                    movie_id = recommendations.iloc[j]['movie_id']
                    match_percentage = recommendations.iloc[j]['match_percentage']
                    match_color = get_match_color(match_percentage)
                    poster_url = fetch_poster(movie_id)
                    
                    with col:
                        st.write(f"**{j+1}. {movie_title}**")
                        if poster_url:
                            st.image(poster_url, width=150)
                        
                        # Display percentage with color coding and progress bar
                        st.markdown(f"<span style='color:{match_color};font-weight:bold'>{match_percentage}% match</span>", unsafe_allow_html=True)
                        st.progress(match_percentage/100)
                        st.write("---")