from fastapi import FastAPI
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import List
from tqdm import tqdm

data = pd.read_csv("normalize_edilmis_dosya.csv")


class SpotifyRecommender:
    def __init__(self, rec_data):
        # our class should understand which data to work with
        self.rec_data_ = rec_data

    # if we need to change data
    def change_data(self, rec_data):
        self.rec_data_ = rec_data

    # function which returns recommendations, we can also choose the amount of songs to be recommended
    def get_recommendations(self, song_name, amount=3):
        distances = []
        # choosing the data for our song
        song = self.rec_data_[(self.rec_data_.name.str.lower() == song_name.lower())].head(1).values[0]
        # dropping the data with our song
        res_data = self.rec_data_[self.rec_data_.name.str.lower() != song_name.lower()]
        for r_song in tqdm(res_data.values):
            dist = 0
            for col in np.arange(len(res_data.columns)):
                # indeces of non-numerical columns
                if not col in [1, 6, 12, 14, 18]:
                    # calculating the manhattan distances for each numerical feature
                    dist = dist + np.absolute(float(song[col]) - float(r_song[col]))
            distances.append(dist)
        res_data['distance'] = distances
        # sorting our data to be ascending by 'distance' feature
        res_data = res_data.sort_values('distance')
        columns = ['artists', 'name']
        return res_data[columns][:amount]


app = FastAPI()

recommender = SpotifyRecommender(data)


class RecommendationsRequest(BaseModel):
    song_name: str


class SpotifySong(BaseModel):
    name: str
    artists: str


class RecommendationsResponse(BaseModel):
    recommendations: List[SpotifySong]


@app.post("/recommendations/", response_model=RecommendationsResponse)
async def get_recommendations(request: RecommendationsRequest):
    song_name = request.song_name
    recommendations = recommender.get_recommendations(song_name)
    return {"recommendations": recommendations.to_dict('records')}
