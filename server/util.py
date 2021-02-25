from flask import Flask, request, jsonify, render_template

import server
import pandas as pd

app = Flask(__name__)


# preparing a list of playlist on which we will base our recommendation
@app.route('/get_my_playlist', methods=['GET', 'POST'])
def get_my_playlist():
    playlist_id = request.form['playlist_id']

    response = server.get_playlist_details(playlist_id, True)
    response = jsonify(response.to_dict(orient='list'))

    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


# get final recommendations using server functions
# this function dose not work very efficiently and takes about 6 min to respond
# still working on making it faster
@app.route('/get_final_playlist', methods=['GET', 'POST'])
def get_final_playlist():
    # playlist of user
    playlist_id = request.form['playlist_id']

    df_my = server.get_playlist_details(playlist_id, True)
    df_my_exploded = server.explode_playlist(df_my)

    df_my_features = server.feature_append(df_my_exploded)

    # playlist to find recommendation from
    recommendation_id = request.form['recommendation_id']

    df_reco = server.get_playlist_details(recommendation_id, True)
    df_reco_exploded = server.explode_playlist(df_reco)

    df_reco_features = server.feature_append(df_reco_exploded)

    # making full data
    full_df = pd.concat([df_my_features, df_reco_features])

    float_cols = full_df.dtypes[full_df.dtypes == 'float64'].index.values
    complete_feature_set = server.create_feature_set(full_df, float_cols=float_cols)  # .mean(axis = 0)

    # making recommendation
    # change name
    playlist_Selected = server.create_necessary_outputs(playlist_id, full_df)
    complete_feature_set_playlist_vector_Selected, complete_feature_set_nonplaylist_Selected = server.generate_playlist_feature(
        complete_feature_set, playlist_Selected, 1.09)

    my_reco = server.generate_playlist_recos(full_df, complete_feature_set_playlist_vector_Selected,
                                             complete_feature_set_nonplaylist_Selected)

    response = jsonify(my_reco.to_dict(orient='list'))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    print("starting process")
    app.run()

# spotify:user:7ur7jjowtivgnatopjff8102l