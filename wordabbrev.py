import re
import pandas as pd
import numpy as np
from itertools import combinations
def read_text_file():
    content_list = []

    read_text_file.filename = input("Enter filename to trees.txt ")

    file = read_text_file.filename + ".txt"

    # Open the file in read mode
    with open(file, 'r') as file:
        # Read all lines from the file and store them in a list
        content_list = file.readlines()
        content_list = [line.strip() for line in content_list]

    return content_list

def Clean_words():
    # Call the function to read the text file and get the content in a list
    original_list = read_text_file()

    # Process the list: convert to uppercase, replace hyphens with whitespace, and remove special characters
    processed_list = [re.sub(r'[^a-zA-Z0-9\s]', '',
                              line.upper().replace('-', ' ')) for line in original_list]
    
    return processed_list

def CreateAbbrevs():
    # Call the previous function to process and generate 3-letter combinations
    processed_content = Clean_words()

    # Check if the processed content is not empty\
    if processed_content:
        # Create an empty list to store unique 3-letter combinations for each item
        unique_combinations_list = []

        # Create an empty dictionary to store the results
        combinations_dict = {}

        # Iterate over each item in the processed content
        for item in processed_content:
            #remove all whitespaces to avoid abbreviations with spaces in them
            word_no_space = item.replace(" ", "")
            # Find all unique 3-letter combinations for the current item
            item_combinations = set([''.join(combination) for combination in combinations(word_no_space, r=3)])

            item_combinations = {c for c in item_combinations if c[0] == word_no_space[0]}

            # Extend the unique_combinations_list with the item combinations
            unique_combinations_list.extend(item_combinations)

            # Store the item name in the dictionary with its combinations as values
            combinations_dict[item] = item_combinations
            
        return combinations_dict


def CalculateScore():
    combinations_dict = CreateAbbrevs()
    #read the values.txt file and store them in a dictionairy 
    values = {}
    with open("values.txt", "r") as file:
                for line in file:
                    letter, value = line.strip().split()
                    values[letter] = int(value)
    #empty list to store results                
    data = []
    # read key value pairs of a dictionairy
    for words, abv_set in combinations_dict.items():
        #split the tree names to consider multiple words within one name
        wordlist = str(words).split()
        #loop through all abbreviations
        for abv in abv_set:
            score = 0
            #store the second and third letter of abbreviation as variables
            second_letter, third_letter = abv[1], abv[2]
            #if either second or third letter match the first letter of the word it came from it gets 0
            if any(second_letter == word[0] for word in wordlist):
                score = 0
            elif any(third_letter == word[0] for word in wordlist):
                score = 0
            else:
                # Calculate the score for the second letter
                if any(second_letter == word[-1] for word in wordlist):
                    score += 20 if second_letter == 'E' else 5
                else:
                    position_value1 = 0
                    for word in wordlist:
                        if abv[1] == word[1]:
                            position_value1 = 1
                            break
                        elif abv[1] == word[2]:
                            position_value1 = 2
                            break
                        elif abv[1] == word[3:]:
                            position_value1 = 3
                            break
                    
                    score += position_value1 + values.get(second_letter)

                # Calculate the score for the third letter
                if any(third_letter == word[-1] for word in wordlist):
                    score += 20 if third_letter == 'E' else 5
                else:
                    position_value2 = 0
                    for word in wordlist:
                        if abv[2] == word[1]:
                            position_value2 = 1
                            break
                        elif abv[2] == word[2]:
                            position_value2 = 2
                            break
                        elif abv[2] == word[3:]:
                            position_value2 = 3
                            break
                    score += position_value2 + values.get(third_letter)

                data.append([words, abv, score])
        #create a dataframe
        df = pd.DataFrame(data, columns=['Tree_Name', 'Abv', 'Score'])


    return df

def FindAbv():
    abv_df = CalculateScore()
    #create a copy of df with tree names and drop all duplicate tree names
    abv_df_copy = abv_df[["Tree_Name"]].copy()
    abv_df_copy = abv_df_copy.assign(acr = '')
    abv_df_copy = abv_df_copy.drop_duplicates(subset = "Tree_Name")
    #drop any rows that had duplicate abbreviations
    abv_df = abv_df.drop_duplicates(subset="Abv", keep = False)
    #get mininimum value for each abbreviation
    min_value = abv_df.groupby('Tree_Name')['Score'].min()
    #
    abv_df = abv_df.merge(min_value, on = "Tree_Name", suffixes = ('', '_min'))
    abv_df = abv_df[abv_df["Score"] == abv_df["Score_min"]].drop('Score_min', axis =1)
    abv_df_diff = abv_df_copy[~abv_df_copy["Tree_Name"].isin(abv_df["Tree_Name"])]
    abv_df_final =  pd.concat([abv_df,abv_df_diff]).sort_index() #concat the missing names
    abv_df_final.drop("Score", axis = 1, inplace=True)
    abv_df_final['Abv'] = abv_df_final[["Tree_Name","Abv"]].groupby(["Tree_Name"])["Abv"].transform(lambda x: ' '.join(map(str, x)))
    abv_df_final = abv_df_final[['Tree_Name','Abv']].drop_duplicates()

    return abv_df_final
# creating a main function to save the output as a txt file
def main():
    final_df = FindAbv()
    output_name = "glica_"+read_text_file.filename+"_abbrevs.txt"
    final_df.to_csv(output_name, sep='\n', encoding="utf-8", index=False, header=False)
main()