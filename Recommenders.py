import numpy as np
import pandas

#Class for Popularity based Recommender System model
class popularity_recommender_py():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.popularity_recommendations = None
        
    #Create the popularity based recommender system model
    def create(self, train_data, user_id, item_id):
        self.train_data = train_data
        self.user_id = user_id
        self.item_id = item_id

        #Get a count of user_ids for each unique product id as recommendation score
        train_data_grouped = train_data.groupby([self.item_id]).agg({self.user_id: 'count'}).reset_index()
        train_data_grouped.rename(columns = {'user_id': 'score'},inplace=True)
    
        #Sort the product ids based upon recommendation score
        train_data_sort = train_data_grouped.sort_values(['score', self.item_id], ascending = [0,1])
    
        #Generate a recommendation rank based upon score
        train_data_sort['Rank'] = train_data_sort['score'].rank(ascending=0, method='first')
        
        #Get the top 10 recommendations
        self.popularity_recommendations = train_data_sort.head(10)

    #Use the popularity based recommender system model to
    #make recommendations
    def recommend(self, user_id):    
        user_recommendations = self.popularity_recommendations
        
        #Add user_id column for which the recommendations are being generated
        user_recommendations['user_id'] = user_id
    
        #Bring user_id column to the front
        cols = user_recommendations.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        user_recommendations = user_recommendations[cols]
        
        return user_recommendations
    

#Class for Item similarity based Recommender System model
class item_similarity_recommender_py():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.cooccurence_matrix = None
        self.songs_dict = None
        self.rev_songs_dict = None
        self.item_similarity_recommendations = None
        
    #Get unique items (products) corresponding to a given user
    def get_user_items(self, user):
        user_data = self.train_data[self.train_data[self.user_id] == user]
        user_items = list(user_data[self.item_id].unique())
        
        return user_items
        
    #Get unique users for a given item (products)
    def get_item_users(self, item):
        item_data = self.train_data[self.train_data[self.item_id] == item]
        item_users = set(item_data[self.user_id].unique())
            
        return item_users
        
    #Get unique items (products) in the training data
    def get_all_items_train_data(self):
        all_items = list(self.train_data[self.item_id].unique())
            
        return all_items
        
    #Construct cooccurence matrix IMPPPPPPPPPPPPPPPPPPPPPPPP
    def construct_cooccurence_matrix(self, user_products, all_products):
            
        ####################################
        #Get users for all products in user_products.
        ####################################
        user_products_users = []
        for i in range(0, len(user_products)):
            user_products_users.append(self.get_item_users(user_products[i]))
            
        ###############################################
        #Initialize the item cooccurence matrix of size 
        #len(user_products) X len(products)
        ###############################################
        cooccurence_matrix = np.matrix(np.zeros(shape=(len(user_products), len(all_products))), float)
           
        #############################################################
        #Calculate similarity between user products and all unique products
        #in the training data
        print(".................................................")
        print(cooccurence_matrix)
        print(".................................................")
        #############################################################
        for i in range(0,len(all_products)):
            #Calculate unique users (users) of products(item) i
            products_i_data = self.train_data[self.train_data[self.item_id] == all_products[i]]
            users_i = set(products_i_data[self.user_id].unique())
            print("USERS_I.................................................")
            print(users_i)
            for j in range(0,len(user_products)):
                    
                #Get unique users(users) of products (item) j
                print("USERS_J.................................................")
                users_j = user_products_users[j]

                print(users_j)
                #Calculate intersection of users of products i and j
                users_intersection = users_i.intersection(users_j)
                print("INTERSECTION.................................................")
                print(users_intersection)
                #Calculate cooccurence_matrix[i,j] as Jaccard Index
                if len(users_intersection) != 0:
                    #Calculate union of users of products i and j
                    users_union = users_i.union(users_j)
                    print("UNION.................................................")
                    print(users_union)
                    cooccurence_matrix[j,i] = float(len(users_intersection))/float(len(users_union))
                else:
                    cooccurence_matrix[j,i] = 0
                    
        
        return cooccurence_matrix

    
    #Use the cooccurence matrix to make top recommendations
    def generate_top_recommendations(self, user, cooccurence_matrix, all_products, user_products):
        print("Non zero values in cooccurence_matrix :%d" % np.count_nonzero(cooccurence_matrix))
        
        #Calculate a weighted average of the scores in cooccurence matrix for all user products.
        user_sim_scores = cooccurence_matrix.sum(axis=0)/float(cooccurence_matrix.shape[0])
        user_sim_scores = np.array(user_sim_scores)[0].tolist()
 
        #Sort the indices of user_sim_scores based upon their value
        #Also maintain the corresponding score
        sort_index = sorted(((e,i) for i,e in enumerate(list(user_sim_scores))), reverse=True)
        print("sorted indexxxx")
        print(sort_index)
        #Create a dataframe from the following
        columns = ['user_id', 'productId', 'score', 'rank']
        #index = np.arange(1) # array of numbers for the number of samples
        df = pandas.DataFrame(columns=columns)
         
        #Fill the dataframe with top 10 item based recommendations
        rank = 1 
        for i in range(0,len(sort_index)):
            if ~np.isnan(sort_index[i][0]) and all_products[sort_index[i][1]] not in user_products and rank <= 10:
                df.loc[len(df)]=[user,all_products[sort_index[i][1]],sort_index[i][0],rank]
                rank = rank+1
        
        #Handle the case where there are no recommendations
        if df.shape[0] == 0:
            print("The current user has no products for training the item similarity based recommendation model.")
            return -1
        else:
            return df
 
    #Create the item similarity based recommender system model
    def create(self, train_data, user_id, item_id):
        self.train_data = train_data
        self.user_id = user_id
        self.item_id = item_id

    #Use the item similarity based recommender system model to
    #make recommendations
    def recommend(self, user):
        
        ########################################
        #A. Get all unique products for this user
        ########################################
        user_products = self.get_user_items(user)
            
        print("No. of unique Products for the user: %d" % len(user_products))
        
        ######################################################
        #B. Get all unique items (products) in the training data
        ######################################################
        all_products = self.get_all_items_train_data()
        
        print("no. of unique products in the training set: %d" % len(all_products))
         
        ###############################################
        #C. Construct item cooccurence matrix of size 
        #len(user_products) X len(products)
        ###############################################
        cooccurence_matrix = self.construct_cooccurence_matrix(user_products, all_products)
        
        #######################################################
        #D. Use the cooccurence matrix to make recommendations
        #######################################################
        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_products, user_products)
                
        return df_recommendations
    
    #Get similar items to given items
    """"
    def get_similar_items(self, item_list):
        
        user_songs = item_list
        
        ######################################################
        #B. Get all unique items (songs) in the training data
        ######################################################
        all_songs = self.get_all_items_train_data()
        
        print("no. of unique songs in the training set: %d" % len(all_songs))
         
        ###############################################
        #C. Construct item cooccurence matrix of size 
        #len(user_songs) X len(songs)
        ###############################################
        cooccurence_matrix = self.construct_cooccurence_matrix(user_songs, all_songs)
        
        #######################################################
        #D. Use the cooccurence matrix to make recommendations
        #######################################################
        user = ""
        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, user_songs)
         
        return df_recommendations
    """