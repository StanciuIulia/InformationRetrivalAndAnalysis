import csv
import math

"""implements a recommender system built from
   a movie list name
   a listing of userid+movieid+rating"""

class Recommender(object):

    #"""initializes a recommender from a movie file and a ratings file"""
    def __init__(self,movie_filename,rating_filename):
        
        """similarity matrix"""
        # similarity matrix between users
        self.similarity_matrix = None
        # similarity matrix between movies
        self.similarity_matrix_movies = None
        
        """parameters for movie recommandation"""
        # number of similar users to base the recommandations on
        self.number_similar_users = 100
        # number of similar movies to base the recommandations on
        self.number_similar_movies = 1000
        
        # read movie file and create dictionary _movie_names
        self._movie_names = {}
        f = open(movie_filename,"r",encoding="utf8")
        reader = csv.reader(f)
        next(reader)  # skips header line
        for line in reader:
            movieid = int(line[0])
            moviename = line[1]
            #moviegenre = line[2]
            self._movie_names[movieid] = moviename
            #self._movie_genres[movieid] = moviegenre
        f.close()
        

        # read rating file and create _movie_ratings (ratings for a movie)
        # and _user_ratings (ratings by a user) dicts
        self._movie_ratings = {}
        self._user_ratings = {}
        f = open(rating_filename,"r",encoding="utf8")
        reader = csv.reader(f)
        next(reader)  # skips header line
        for line in reader:
            userid = int(line[0])
            movieid = int(line[1])
            rating = float(line[2])
            # ignore line[3], timestamp

            if userid in self._user_ratings:
                self._user_ratings[userid].append((movieid,rating))
            else:
                self._user_ratings[userid] = [(movieid,rating)]

            if movieid in self._movie_ratings:
                self._movie_ratings[movieid].append((userid,rating))
            else:
                self._movie_ratings[movieid] = [(userid,rating)]    
        f.close

    """returns a list of pairs (userid,rating) of users that
       have rated movie movieid"""
    def get_movie_ratings(self,movieid):
        return self._movie_ratings[movieid] if movieid in self._movie_ratings else  None

    """returns a list of pairs (movieid,rating) of movies
       rated by user userid"""
    def get_user_ratings(self,userid):
        return self._user_ratings[userid] if userid in self._user_ratings else None
       
    """returns the list of user id's in the dataset"""
    def userid_list(self):
        return self._user_ratings.keys()

    """returns the list of movie id's in the dataset"""
    def movieid_list(self):
        return self._movie_ratings.keys()
    
    """returns the number of movies in the dataset"""
    def movieid_count(self):
        return len(self._movie_names)
    
    """returns the number of users in the dataset"""
    def userid_count(self):
        return len(self._user_ratings.keys())
    
    """returns the name of movie with id movieid"""
    def movie_name(self,movieid):
        return self._movie_names[movieid] if movieid in self._movie_names else None

    
    """calculates and returns the cosine similarity""" 
    def cosine_similarity(self,v1,v2):
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]; y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        denominator = math.sqrt(sumxx*sumyy)                                           
        return sumxy/denominator if denominator > 0 else 0


    """
    User to user similarity functions
    -----------------------------------------------------------------------------------------------------------------------------------------
    """
        
    """calculates and returns the cosine similarity between two users""" 
    def get_sim_2_users(self, user1_rating_list, user2_rating_list):

        movie_ids_1, ratings_1 = [x[0] for x in user1_rating_list], [x[1] for x in user1_rating_list]
        movie_ids_2, ratings_2 = [x[0] for x in user2_rating_list], [x[1] for x in user2_rating_list]    
        
        movie_intersection = []
        ratings_int_1 = []
        ratings_int_2 = []
        
        for i in range (len(movie_ids_1)):
            selected_id = movie_ids_1[i]
            if(selected_id in movie_ids_2):
                movie_intersection.append(selected_id)
                ratings_int_1.append(ratings_1[i])
                ratings_int_2.append(ratings_2[movie_ids_2.index(selected_id)])        
        
        #return ratings_int_1, ratings_int_2
        return self.cosine_similarity(ratings_int_1, ratings_int_2)
        
    """calculate the cosine similarity between all users and stores it in the similarity matrix for users"""   
    def calculate_similarity(self, userids = None):
        if(self.similarity_matrix is None):
            self.similarity_matrix = {} 
        if(userids is None):
            userids = self._user_ratings
        for userid1 in userids:
            self.similarity_matrix[userid1] = []
            for userid2 in self._user_ratings:
                self.similarity_matrix[userid1].append(
                    self.get_sim_2_users(self._user_ratings[userid1], self._user_ratings[userid2]))
    
    """calculate the movies' predicted score and which movies are the best for a user based on the most similar users""" 
    def get_movie_predicted_score(self, userids):
        similarity_scores = []
        for userid in userids:
            self.calculate_similarity(userids = [userid])
            similarity_scores = self.similarity_matrix[userid]
            userids_vector = [x for x in range(1, len(similarity_scores)+1)]
        
        zipped = sorted(zip(similarity_scores, userids_vector))
        similarity_scores_sorted = [y for y, x in zipped][::-1][0:self.number_similar_users]
        userids_vector_sorted = [x for y, x in zipped][::-1][0:self.number_similar_users]
        #print(similarity_scores_sorted, userids_vector_sorted)
        
        min_sim = similarity_scores_sorted[-1]
        max_sim = similarity_scores_sorted[0]
        
        if(max_sim != min_sim):
            similarity_scores_sorted = list(map(lambda x: (x-min_sim)/(max_sim-min_sim), similarity_scores_sorted))
        
        #print(similarity_scores_sorted)
        
        movie_scores = {}
        similarity_score_sum={}
        for movieid in self.movieid_list():
            movie_scores[movieid] = 0
            similarity_score_sum[movieid] = 0
            
        for index in range(len(userids_vector_sorted)):
            user_rating_list = self.get_user_ratings(userids_vector_sorted[index])
            movie_ids, ratings = [x[0] for x in user_rating_list], [x[1] for x in user_rating_list]
            
            for i in range(len(movie_ids)):
                movie_scores[movie_ids[i]] += similarity_scores_sorted[index]*ratings[i]
                similarity_score_sum[movie_ids[i]] += similarity_scores_sorted[index]
        
        recommandations_scores = movie_scores
        recommandation_scores_sorted = dict(sorted(recommandations_scores.items(), key=lambda item: item[1], reverse = True))
        
        #print([x for x in recommandation_scores_sorted.values() if x > 0])
        #print(recommandation_scores_sorted[333])
        #print(recommandation_scores_sorted[318])
        #print(recommandation_scores_sorted[1704])
        
        for movieid in self.movieid_list():
            #normalize movie scores
            total_sum = similarity_score_sum[movieid]
            if(total_sum > 0):
                movie_scores[movieid] /= total_sum   
        #print([x for x in movie_scores.values() if x > 0])
        #print(max(movie_scores.values()), min(movie_scores.values()))
        
        #remove movies that user has already seen
        for movieid in movie_ids:
            if(movieid in recommandation_scores_sorted.keys()):
                recommandation_scores_sorted.pop(movieid)
            
        return recommandation_scores_sorted, movie_scores
        
            
    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_user_to_user(self,rating_list,k):
        recommended_movies = []
        
        new_id = self.userid_count()+1
        self._user_ratings[new_id] = rating_list;
        recommandation_scores_sorted, movie_scores = self.get_movie_predicted_score(userids = [new_id])
        
        
        if(k < len(recommandation_scores_sorted)):
            resized_recommandation_list = dict(list(recommandation_scores_sorted.items())[0:k])
        else: 
            resized_recommandation_list = recommandation_scores_sorted
            
        for movieid in resized_recommandation_list:
            recommended_movies.append((movieid, movie_scores[movieid], round(movie_scores[movieid] * 2)/2))
        
        return recommended_movies

    """
    Item to item similarity functions
    -----------------------------------------------------------------------------------------------------------------------------------------
    """

    """calculates and returns the cosine similarity between two movies""" 
    def get_sim_2_movies(self, movie1_rating_list, movie2_rating_list):

        user_ids_1, ratings_1 = [x[0] for x in movie1_rating_list], [x[1] for x in movie1_rating_list]
        user_ids_2, ratings_2 = [x[0] for x in movie2_rating_list], [x[1] for x in movie2_rating_list]    
        
        ratings_int_1 = [0]*self.userid_count()
        ratings_int_2 = [0]*self.userid_count()
        
        for i in range (len(user_ids_1)):
            ratings_int_1[user_ids_1[i]] = ratings_1[i]
        
        for j in range (len(user_ids_2)):
            ratings_int_2[user_ids_2[j]] = ratings_2[j]      
        
        #return ratings_int_1, ratings_int_2
        return self.cosine_similarity(ratings_int_1, ratings_int_2)
    
    """calculate the cosine similarity between all movies and stores it in the similarity matrix for movies"""   
    def calculate_similarity_matrix_movies(self, movieids = None):

        if(self.similarity_matrix_movies is None):
            self.similarity_matrix_movies = {} 

        if(movieids is None):
            movieids = self._movie_ratings

        for movie1 in movieids:
            self.similarity_matrix_movies[movie1] = []
            for movie2 in self._movie_ratings:
                self.similarity_matrix_movies[movie1].append(
                    self.get_sim_2_movies(self._movie_ratings[movie1], self._movie_ratings[movie2]))
    
    def average_rating(self, movieid):

        average = 0
        movie_ratings = self.get_movie_ratings(movieid)
        ratings = [x[1] for x in movie_ratings]
        average = sum(ratings)/len(ratings)
        return average
    
    """calculate the movies' predicted score and which movies are the best for a user based on the movies watched by the user""" 
    def get_movie_predicted_score_moviebased(self, movieids, userid):
        
        user_ratings = self.get_user_ratings(userid)
        movie_ids = [x[0] for x in user_ratings]
        
        similarity_scores = []
        for movieid in movieids:
            movie_rating = [item[1] for item in user_ratings if item[0] == movieid]
            movie_rating_by_user = movie_rating[0]
            self.calculate_similarity_matrix_movies(movieids = [movieid])
            similarity_scores = self.similarity_matrix_movies[movieid]
            movieids_vector = self.movieid_list()
        
        zipped = sorted(zip(similarity_scores, movieids_vector))
        similarity_scores_sorted = [y for y, x in zipped][::-1][0:self.number_similar_movies]
        movieids_vector_sorted = [x for y, x in zipped][::-1][0:self.number_similar_movies]
        #print(similarity_scores_sorted, movieids_vector_sorted)
        
        min_sim = similarity_scores_sorted[-1]
        max_sim = similarity_scores_sorted[0]
        
        if(max_sim != min_sim):
            similarity_scores_sorted = list(map(lambda x: (x-min_sim)/(max_sim-min_sim), similarity_scores_sorted))
        #print(similarity_scores_sorted, movieids_vector_sorted)
        
        movie_scores = {}
        for movieid in self.movieid_list():
            movie_scores[movieid] = 0
            
        for index in range(len(movieids_vector_sorted)):
            movie = movieids_vector_sorted[index]
            #similarity score = probability that the movies will be rated equaly by the user = p
            #expected movie score = (1 - p)*average_rating_movie_to_be_seen + p*rating_seen_movie
            movie_scores[movie] = (1 - similarity_scores_sorted[index])*float(self.average_rating(movie)) + \
                    similarity_scores_sorted[index]*movie_rating_by_user
            
        recommandation_scores = {}
        for movieid in movieids_vector_sorted:
            recommandation_scores[movieid] = similarity_scores_sorted
            
        for movieid in movie_ids:
            if(movieid in recommandation_scores.keys()):
                recommandation_scores.pop(movieid)
            
        return recommandation_scores, movie_scores
 
        
    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_item_to_item(self,rating_list,k):
        recommended_movies = []
        
        new_id = self.userid_count()+1
        self._user_ratings[new_id] = rating_list
        rating_list_ordered = sorted(rating_list, key=lambda x:x[1], reverse=True)
        movies = [tup[0] for tup in rating_list_ordered]
        movieid = movies[0]
        recommandation_scores_sorted, movie_scores = self.get_movie_predicted_score_moviebased([movieid], new_id)
        
        if(k < len(recommandation_scores_sorted)):
            resized_recommandation_list = dict(list(recommandation_scores_sorted.items())[0:k])
        else: 
            resized_recommandation_list = recommandation_scores_sorted
            
        for movieid in resized_recommandation_list:
            estimated_rating = movie_scores[movieid]
            recommended_movies.append((movieid, estimated_rating, round(estimated_rating * 2)/2))
        
        return recommended_movies

    """ 
    Printing functions
    -----------------------------------------------------------------------------------------------------------------------------------------
    """
    
    """prints the names and ratings of the movies seen by user"""
    def print_movies_seen(self, movies_list):
        for index in range(len(movies_list)):
            temp = movies_list[index]
            print("Movie:", self._movie_names[temp[0]], "with a rating of", temp[1])
    
    """prints the names and predicted rating of the recommended movies"""
    def print_recommandations(self, recommended_movies_list):
        print("The", len(recommended_movies_list), "movie recommandations are:")
        for index in range(len(recommended_movies_list)):
            temp = recommended_movies_list[index]
            print("Movie:", self._movie_names[temp[0]], "with a rating of", temp[1], "rounded to", temp[2])

def main():
    r = Recommender("movies.csv","ratings.csv")
    r.calculate_similarity(userids = [2])
    
    print("User 2 recommended movies ")
    r.print_movies_seen(r.get_user_ratings(2))
    
    print()
    r.print_recommandations(r.recommend_user_to_user(r.get_user_ratings(2), 10))

    print()
    r.print_recommandations(r.recommend_item_to_item(r.get_movie_ratings(333), 10))
    
main()


