

from ga.algorithm import Algorithm
from sqlalchemy.orm import Session
from fastapi import Depends
import numpy as np
import math
from collections import Counter

from db.database import get_db
from db.repositories import UserRepository, MovieRepository, RatingsRepository

class MyGeneticAlgorithm(Algorithm):

    def __init__(self, query_search, individual_size, population_size, p_crossover, p_mutation, all_ids, max_generations=100, size_hall_of_fame=1, fitness_weights=(1.0, ), seed=42, db=None) -> None:


        super().__init__(
            individual_size, 
            population_size, 
            p_crossover, 
            p_mutation, 
            all_ids, 
            max_generations, 
            size_hall_of_fame, 
            fitness_weights, 
            seed)
        
        self.db = db
        self.all_ids = all_ids
        self.query_search = query_search

        # User data
        rated_movies = RatingsRepository.find_by_userid(self.db, self.query_search)
        self.watched_movies = [movie.movie.movieId for movie in rated_movies] # Watched movies IDs

        least_liked_genres = set()
        most_liked_genres = set()

        for m in rated_movies:
            genres = m.movie.genres.split('|')
            if m.rating <= 2:
                least_liked_genres.update(genres)
            elif m.rating >= 4:
                most_liked_genres.update(genres)

        # Get the top 3 most and least liked genres
        top_ll_genres = Counter(least_liked_genres).most_common(3)
        top_ml_genres = Counter(most_liked_genres).most_common(3)

        self.least_liked_genres_list = [genre for genre, count in top_ll_genres]
        self.most_liked_genres_list = [genre for genre, count in top_ml_genres]

        
    def evaluate(self, individual):

        if len(individual) != len(set(individual)) or set(individual) - set(self.all_ids):
            return (0.0, )

        points = []
        
        for title in individual:
            current_title = MovieRepository.find_by_id(self.db, title)
            current_title_genres = set(current_title.genres.split('|'))
            
            if title in self.watched_movies:
                if current_title_genres.intersection(set(self.least_liked_genres_list)):
                    points.append(-10)
                elif current_title_genres.intersection(set(self.most_liked_genres_list)):
                    points.append(70)
                else:
                    points.append(60)
            else:
                if current_title_genres.intersection(set(self.least_liked_genres_list)):
                    points.append(0)
                elif current_title_genres.intersection(set(self.most_liked_genres_list)):
                    points.append(100)
                else:
                    points.append(70)

        score = sum(points) if individual else 0.0
        return (score, )
