#
# Name: varSelector.py
# Author: Marcello Coletti
# Contact: coletti.marcello@gmail.com
# USFQ Data Hub
#

# This program returns a an excel file with cosine similarity analysis between 
# a set of variables description. This is because some Data Bases doesn't have
# clear specifications about their variables and they could contain different names
# for a same variable in all the files of the Data Base. With this program I aim to avoid 
# to test variable per variable.

### This program requires textSimilarity.py and csv_tolist.py

import numpy as np
from os import system

class Selector:
    
    def __init__(self, id, files_directory):
        self.id = id # The id is the Data Base name, example: ENEMDU
        self.files_directory = files_directory # The directory of the csv files of the Data Base
        
        self.files = [] # Will save the name of the csv files contents in self.files_directory.
        self.files_names() # To assemble self.files
        
        self.presence = [None]*len(self.files)  # Will be the table of in which csv file is present a variable.
                                                # The value will be 1 if the variable (column) is in the file (row)
        self.all_var_names = [] # Represent the vector of all the variables names in all the csv files
        self.encodings = [None]*len(self.files) # Represent the vector of the encodings of the csv files.
        self.get_var_names() # To assemble self.all_var_names
        
        self.vars_description = []  # Represent the vector of the description for each variable in the description file and 
                                    # self.all_var_names vector
        self.var_names = [] # Represent the vector of the variable names for each variable in the description file and 
                            # self.all_var_names vector
        self.get_vars_description() # To assemble self.var_names and self.vars_description
        
        from textSimilarity import Similarity

        system('clear')
        print('Starting Similarity analysis. It could take more time to be finished.')
        self.similarity = Similarity(id, self.vars_description, self.var_names) # Calculate the cosine similarity between the 
                                                                                # variables description.
        self.similarity_summary = self.similarity.__str__()
        self.similarity_matrix = self.similarity.similarity_matrix # Retrieve the cosine similarity matrix
        
        self.same_vars = [] # Vetor of selected pairs at some choosen cosine similarity level (0.3 by default)
        self.non_repeated_vars() # To assemble self.same_vars

        system('clear')
        self.summary = self.__str__()
        self.summary
        
    def __str__(self):
        print(f'\n{self.id}:\n',
              f'\nTotal files read: {len(self.files)}',
              f'\n{self.id}\n',
              f'Same vars: '
              f'\n{self.same_vars} \n')
        
    def files_names(self):
        from os import listdir
        self.files = listdir(self.files_directory)
        
    def comparation(self, target_list):
        current_list = self.all_var_names.copy()
        in_list = [0]*len(current_list)
        
        for k in range(len(target_list)):
            if target_list[k] not in current_list:
                self.all_var_names.append(target_list[k])
                in_list.append(1)
        
        for j in range(len(current_list)):
            if current_list[j] in target_list:
                in_list[j] = 1
            
        return in_list

    def get_var_names(self):
        from csv_tolist import get_csv_varnames
        
        for i in range(len(self.files)):
            system('clear')
            print("opening "+self.files[i])
            
            if self.files[i][-4:] == '.csv':
                
                var_names, self.encodings[i] = get_csv_varnames(self.files_directory+'\\'+self.files[i])
                
                new_row = self.comparation(var_names)
                self.presence[i] = new_row
                
            else:
                print("Bad file \n")
                print(self.files[i])
                
        for j in range(len(self.presence)):
            self.presence[j].extend([0]*(len(self.all_var_names)-len(self.presence[j])))
                
        self.presence = np.array(self.presence)

    def get_vars_description(self):
        system('clear')
        print('Opening description file')
        my_file = open(f'{self.id.lower()}_var_names_description.csv', "r")

        data = my_file.read()
        rows = data.split("\n")
        for i in range(len(rows)):
            rows[i] = rows[i].split(",")
            if rows[i][0] in self.all_var_names:
                self.vars_description.append(rows[i][1])
                self.var_names.append(rows[i][0])
        
        my_file.close()

    def non_repeated_vars(self, proportion = 0.3):
        
        self.same_vars = []
        
        for pairs in self.similarity.values:
            pair = pairs.split('/')
            
            if pair[0] != pair[1] and self.similarity.values[pairs] >= proportion:
                numbers_list = [None]*len(self.presence)
                pair1 = self.all_var_names.index(pair[0])
                pair2 = self.all_var_names.index(pair[1])
                
                numbers_list = self.presence[:,pair1] + self.presence[:,pair2]
                
                if np.amax(numbers_list) == 1 and np.amin(numbers_list) == 1:
                    self.same_vars.append(pairs)

    def to_excel(self):
        
        repeated_vars = [None]*100
        
        proportion_level = [(x+1)/100 for x in range(100)]
        for i in range(100):
            self.non_repeated_vars(proportion_level[i])
            repeated_vars[i] = ' '.join(self.same_vars)

        import pandas as pd
        all_pairs = pd.DataFrame(columns=[])
        all_pairs['proportion'] = pd.Series(proportion_level)
        all_pairs['pairs'] = pd.Series(repeated_vars)
        all_pairs = all_pairs.set_index('proportion')
        
        system('clear')
        print("Exporting results to excel file: "+f'{self.id.lower()}_vars_similarity.xlsx')
              
        presence_df = pd.DataFrame(self.presence,
                        index=self.files,
                        columns=self.all_var_names)

        similarity_df = pd.DataFrame(self.similarity_matrix,
                        index=self.var_names,
                        columns=self.var_names)
        encodings_df = pd.DataFrame(columns=[])
        encodings_df['file'] = pd.Series(self.files)
        encodings_df['encoding'] = pd.Series(self.encodings)
        encodings_df = encodings_df.set_index('file')

        writer = pd.ExcelWriter(f'{self.id.lower()}_vars_similarity.xlsx', engine='openpyxl')

        presence_df.to_excel(writer, sheet_name='presence')
        similarity_df.to_excel(writer, sheet_name='similarity')
        all_pairs.to_excel(writer, sheet_name='pairs')
        encodings_df.to_excel(writer, sheet_name='encodings')

        writer.save()