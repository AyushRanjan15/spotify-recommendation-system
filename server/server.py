
# IMPORTS
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

import pandas as pd
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

import warnings

warnings.filterwarnings("ignore")

# setting variables for authorization
client_id = '2ab55afd64cd4a9a86bb74e93a4f75f5'
client_secret = '20d4708024db41d6a193b4d03e08d55e'
scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

# auth from spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

token = util.prompt_for_user_token(scope, client_id=client_id, client_secret=client_secret,
                                   redirect_uri='http://google.com/')
sp = spotipy.Spotify(auth=token)


def get_playlist_details(playlist_id, add_images):
    """
    Create a DF detailing songs artist/album/image of every song in playlist.

    Parameters:
        playlist_id (str): Spotify playlist URI
        add_images (boolean): set true if you want to add images to result df

    Returns:
        result: pd df containing album_name/song_name/song_cover_pic... of all songs in provided playlist.
    """

    p_list = sp.playlist(playlist_id=playlist_id)

    # make a df and get song/ song uri/ artist/ artist uri
    album_names = []
    all_artists = []
    all_song_name = []
    all_song_uri = []
    all_album_uri = []
    all_artists_uri = []
    all_image_link = []

    all_songs = p_list['tracks']['items']

    for song in all_songs:
        # add images url to df if add_image = True
        if (add_images):
            img = song['track']['album']['images'][0]['url']
            all_image_link.append(img)

        # pulling song names
        curr_song_name = song['track']['name']
        all_song_name.append(curr_song_name)

        # song uri
        curr_song_uri = song['track']['uri'].split(':')[2]
        all_song_uri.append(curr_song_uri)

        # pulling all album names
        curr_album_name = song['track']['album']['name']
        album_names.append(curr_album_name)

        # album uri
        curr_album_uri = song['track']['album']['uri'].split(':')[2]
        all_album_uri.append(curr_album_uri)

        # pulling all artist name & uri
        #         artists_temp = []
        artists_uri = []
        song_artists = song['track']['album']['artists']
        for artist in song_artists:
            #             artists_temp.append(artist['name'])
            artists_uri.append(artist['uri'].split(':')[2])

        #         all_artists.append(artists_temp)
        all_artists_uri.append(artists_uri)

    if (add_images):
        result = pd.DataFrame({
            'album_name': album_names,
            'album_uri': all_album_uri,
            #     'artist_name' : all_artists,
            'artist_uri': all_artists_uri,
            'song_name': all_song_name,
            'song_uri': all_song_uri,
            'img_link': all_image_link
        })
    else:
        result = pd.DataFrame({
            'album_name': album_names,
            'album_uri': all_album_uri,
            # 'artist_name' : all_artists,
            'artist_uri': all_artists_uri,
            'song_name': all_song_name,
            'song_uri': all_song_uri
        })

    return result


def explode_playlist(df):
    """
    some songs have multiple artists, by exploding df we will have only one value in artist_uri and multiple copy
    of songs if it has more than 1 artist.

    we add name of each artist and their genre with the exploded df

    :param df: Data Frame to be exploded
    :return: exploded df
    """
    df = df.explode('artist_uri')

    df['artist_name'] = df['artist_uri'].apply(lambda x: sp.artist(x)['name'])
    df['artist_genres'] = df['artist_uri'].apply(lambda x: sp.artist(x)['genres'])

    return df


def feature_append(a):
    """
    append audio_features provided by spotify to every song in df.
    append
    :param a: df to append features to
    :return: final df with all features
    """
    a['danceability'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['danceability'])
    a['energy'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['energy'])
    a['mode'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['mode'])
    a['speechiness'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['speechiness'])
    a['acousticness'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['acousticness'])
    a['instrumentalness'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['instrumentalness'])
    a['liveness'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['liveness'])
    a['tempo'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['tempo'])
    a['duration_ms'] = a['song_uri'].apply(lambda x: sp.audio_features(x)[0]['duration_ms'])

    # add other features
    a['release_date'] = a['song_uri'].apply(lambda x: sp.track(x)['album']['release_date'])
    a['popularity'] = a['song_uri'].apply(lambda x: sp.track(x)['popularity'])

    # create 5 point buckets for popularity
    a['popularity_red'] = a['popularity'].apply(lambda x: int(x / 5))
    # tfidf does not expect null values so we will so this check
    a['artist_genres'] = a['artist_genres'].apply(lambda d: d if isinstance(d, list) else [])

    a['release_date'] = a['release_date'].apply(lambda x: x.split('-')[0])
    a['release_date'] = a['release_date'].astype('int')

    return a


# simple function to create OHE features
def ohe_prep(df, column, new_name):
    """
    Create One Hot Encoded features of a specific column

    Parameters:
        df (pandas dataframe): Spotify Dataframe
        column (str): Column to be processed
        new_name (str): new column name to be used

    Returns:
        tf_df: One hot encoded features
    """

    tf_df = pd.get_dummies(df[column])
    feature_names = tf_df.columns
    tf_df.columns = [new_name + "|" + str(i) for i in feature_names]
    tf_df.reset_index(drop=True, inplace=True)
    return tf_df


# function to build entire feature set
def create_feature_set(df, float_cols):
    """
    Process spotify df to create a final set of features that will be used to generate recommendations

    Parameters:
        df (pandas dataframe): Spotify Dataframe
        float_cols (list(str)): List of float columns that will be scaled

    Returns:
        final: final set of features
    """
    # tfidf genre lists
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['artist_genres'].apply(lambda x: " ".join(x)))
    genre_df = pd.DataFrame(tfidf_matrix.toarray())
    genre_df.columns = ['genre' + "|" + i for i in tfidf.get_feature_names()]
    genre_df.reset_index(drop=True, inplace=True)

    # explicity_ohe = ohe_prep(df, 'explicit','exp')
    year_ohe = ohe_prep(df, 'release_date', 'year') * 0.5
    popularity_ohe = ohe_prep(df, 'popularity_red', 'pop') * 0.15

    # scale float columns
    floats = df[float_cols].reset_index(drop=True)
    scaler = MinMaxScaler()
    floats_scaled = pd.DataFrame(scaler.fit_transform(floats), columns=floats.columns) * 0.2

    # concanenate all features
    final = pd.concat([genre_df, floats_scaled, popularity_ohe, year_ohe], axis=1)

    # add song id
    final['id'] = df['song_uri'].values

    return final


def create_necessary_outputs(play_id, df):
    """
    Pull songs from a specific playlist.

    Parameters:
        playlist_name (str): name of the playlist you'd like to pull from the spotify API
        id_dic (dic): dictionary that maps playlist_name to playlist_id
        df (pandas dataframe): spotify datafram

    Returns:
        playlist: all songs in the playlist THAT ARE AVAILABLE IN THE KAGGLE DATASET
    """

    # generate playlist dataframe
    playlist = pd.DataFrame()

    for ix, i in enumerate(sp.playlist(play_id)['tracks']['items']):
        # print(i['track']['artists'][0]['name'])
        playlist.loc[ix, 'artist'] = i['track']['artists'][0]['name']
        playlist.loc[ix, 'name'] = i['track']['name']
        playlist.loc[ix, 'id'] = i['track']['id']  # ['uri'].split(':')[2]
        playlist.loc[ix, 'url'] = i['track']['album']['images'][1]['url']
        playlist.loc[ix, 'date_added'] = i['added_at']

    playlist['date_added'] = pd.to_datetime(playlist['date_added'])

    playlist = playlist[playlist['id'].isin(df['song_uri'].values)].sort_values('date_added', ascending=False)

    return playlist


def generate_playlist_feature(complete_feature_set, playlist_df, weight_factor):
    """
    Summarize a user's playlist into a single vector

    Parameters:
        complete_feature_set (pandas dataframe): Dataframe which includes all of the features for the spotify songs
        playlist_df (pandas dataframe): playlist dataframe
        weight_factor (float): float value that represents the recency bias. The larger the recency bias, the most priority recent songs get. Value should be close to 1.

    Returns:
        playlist_feature_set_weighted_final (pandas series): single feature that summarizes the playlist
        complete_feature_set_nonplaylist (pandas dataframe):
    """

    complete_feature_set_playlist = complete_feature_set[
        complete_feature_set['id'].isin(playlist_df['id'].values)]  # .drop('id', axis = 1).mean(axis =0)
    complete_feature_set_playlist = complete_feature_set_playlist.merge(playlist_df[['id', 'date_added']], on='id',
                                                                        how='inner')
    complete_feature_set_nonplaylist = complete_feature_set[
        ~complete_feature_set['id'].isin(playlist_df['id'].values)]  # .drop('id', axis = 1)

    playlist_feature_set = complete_feature_set_playlist.sort_values('date_added', ascending=False)

    most_recent_date = playlist_feature_set.iloc[0, -1]

    for ix, row in playlist_feature_set.iterrows():
        playlist_feature_set.loc[ix, 'months_from_recent'] = int(
            (most_recent_date.to_pydatetime() - row.iloc[-1].to_pydatetime()).days / 30)

    playlist_feature_set['weight'] = playlist_feature_set['months_from_recent'].apply(lambda x: weight_factor ** (-x))

    playlist_feature_set_weighted = playlist_feature_set.copy()
    # print(playlist_feature_set_weighted.iloc[:,:-4].columns)
    playlist_feature_set_weighted.update(
        playlist_feature_set_weighted.iloc[:, :-4].mul(playlist_feature_set_weighted.weight, 0))
    playlist_feature_set_weighted_final = playlist_feature_set_weighted.iloc[:, :-4]
    # playlist_feature_set_weighted_final['id'] = playlist_feature_set['id']

    return playlist_feature_set_weighted_final.sum(axis=0), complete_feature_set_nonplaylist


def generate_playlist_recos(df, features, nonplaylist_features):
    """
    Pull songs from a specific playlist.

    Parameters:
        df (pandas dataframe): spotify dataframe
        features (pandas series): summarized playlist feature
        nonplaylist_features (pandas dataframe): feature set of songs that are not in the selected playlist

    Returns:
        non_playlist_df_top_40: Top 40 recommendations for that playlist
    """

    non_playlist_df = df[df['song_uri'].isin(nonplaylist_features['id'].values)]
    non_playlist_df['sim'] = cosine_similarity(nonplaylist_features.drop('id', axis=1).values,
                                               features.values.reshape(1, -1))[:, 0]
    non_playlist_df_top_40 = non_playlist_df.sort_values('sim', ascending=False).head(40)
    non_playlist_df_top_40['url'] = non_playlist_df_top_40['song_uri'].apply(
        lambda x: sp.track(x)['album']['images'][1]['url'])

    return non_playlist_df_top_40



# spotify:user:7ur7jjowtivgnatopjff8102l
