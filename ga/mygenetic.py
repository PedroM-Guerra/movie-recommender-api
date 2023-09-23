

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
        

    # O individual é formado por uma lista de IDs dos filmes

    def evaluate(self, individual):

        if len(individual) != len(set(individual)):
            return (0.0, )
        
        if len(list(set(individual) - set(self.all_ids))) > 0:
            return (0.0, )
        
        # Lista dos objetos dos filmes
        movies = MovieRepository.find_all_ids(self.db, individual)

        # Dados filmes na lista individual
        ratings_movies = RatingsRepository.find_by_movieid_list(self.db, individual)
        genres_movies = list(set(genre for movie in movies for genre in movie.genres.split('|')))

        # User data
        rated_movies = RatingsRepository.find_by_userid(self.db, 1)

        least_liked_genres_list = [genre for m in rated_movies if m.rating <= 2 for genre in m.movie.genres.split('|')]
        most_liked_genres_list = [genre for m in rated_movies if m.rating >= 4 for genre in m.movie.genres.split('|')]

        l_genre_counts = Counter(least_liked_genres_list)
        m_genre_counts = Counter(most_liked_genres_list)

        top_ll_genres = l_genre_counts.most_common(3)
        top_ml_genres = m_genre_counts.most_common(3)

        least_liked_genres_list = [genre for genre, count in top_ll_genres]
        most_liked_genres_list = [genre for genre, count in top_ml_genres]


        if len(ratings_movies) > 0:
            mean_ = np.mean([obj_.rating for obj_ in ratings_movies])
        else:
            mean_ = 0.0

        return (mean_, )

