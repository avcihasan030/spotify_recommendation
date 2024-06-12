from fastapi import FastAPI
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import List
from tqdm import tqdm

data = pd.read_csv("normalize_edilmis_dosya.csv")


class SpotifyRecommender:
    def __init__(self, rec_data):
        self.rec_data_ = rec_data

    def change_data(self, rec_data):
        self.rec_data_ = rec_data

    def get_recommendations(self, song_names: List[str], amount=3):
        recommendations = []
        for song_name in song_names:
            distances = []
            song = self.rec_data_[(self.rec_data_.name.str.lower() == song_name.lower())].head(1).values[0]
            res_data = self.rec_data_[self.rec_data_.name.str.lower() != song_name.lower()]
            for r_song in tqdm(res_data.values):
                dist = 0
                for col in np.arange(len(res_data.columns)):
                    if not col in [1, 6, 12, 14, 18]:
                        dist = dist + np.absolute(float(song[col]) - float(r_song[col]))
                distances.append(dist)
            res_data['distance'] = distances
            res_data = res_data.sort_values('distance')
            columns = ['artists', 'name']
            recommendations.extend(res_data[columns][:amount].to_dict('records'))
        return recommendations


app = FastAPI()

recommender = SpotifyRecommender(data)


class RecommendationsRequest(BaseModel):
    song_names: List[str]


class SpotifySong(BaseModel):
    name: str
    artists: str


class RecommendationsResponse(BaseModel):
    recommendations: List[SpotifySong]


@app.post("/recommendations/", response_model=RecommendationsResponse)
async def get_recommendations(request: RecommendationsRequest):
    song_names = request.song_names
    recommendations = recommender.get_recommendations(song_names)
    return {"recommendations": recommendations}