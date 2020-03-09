#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 20:12:34 2020

@author: StephenBlackwell
"""
import functools
from itertools import combinations 
from random import randint
import pandas as pd
#import numpy as np
import matplotlib.pyplot as plt


def getWords(fileName = ""):
    words = []
    while len(words) == 0:
        try: 
            x = int(input("Word Length: "))
            posVals = list(range(x))
            for line in open(fileName, 'r'):
                word = line.strip()
                if len(word) == x:
                    words.append(word)
            if len(words) == 0:
                print("Not a valid word length")
        except ValueError:
            print("Not a valid number")
    return words, posVals, x
    
def getGuesses():
    guesses = 0
    while not (guesses > 0):
        try: 
            guesses = int(input("Guesses: "))
            if guesses <= 0:
                print("Enter a number larger than 0")
        except ValueError:
            print("Not a valid number")
    return guesses

def getYN(inputString = ""):
    while True:       
        useShowWords = input(inputString)
        if useShowWords == "yes":
            return True
        if useShowWords == "no":
            return False
        print("Input not recognized, please type either 'yes' or 'no' with no quotation marks")

def getCategories(posVals = []):
    categories = []
    #Loop through every possible length of combinations
    for i in range(len(posVals) + 1):
        #Loop through all the combinations of a certain length
        for item in combinations(posVals, i):
            categories.append(item)
    #Order from smallest to largest
    categories = sorted(categories, key=len)
    #Reverse to largest to smallest
    categories.reverse()
    return categories

def findBestWords(words = [], posVals = [], guess = ""):
    bestCat = []
    bestWords = []
    categoryWords = {}
    #Get possible categories
    categories = getCategories(posVals)
    #Loop every possible combination of position locations, largest to smallest
    for category in categories:
        catWords = []
        #Loop every word and check for a match
        for word in words.copy():
            fits = True
            #For no match
            if len(category) == 0:
                if guess in word:
                    fits = False
            #For match
            else:
                for i in category:
                    if word[i] != guess:
                        fits = False
            #Add to category specific list
            if fits:
                catWords.append(word)  
                words.remove(word)
        #Add the selection of words to the dictionary
        categoryWords[category] = [catWords]
    #Find the best value 
    largestLen = 0
    bestValues = []
    found = True
    #Loop through the values
    for key, value in categoryWords.items():
        usedValues = []
        for num in key:
            usedValues.append(num)
        x = len(value[0])
        if x >= largestLen:
            largestLen, bestValues = x, key
    #Check if the best result is letting them find a value   
    if len(bestValues) == 0:
        found= False
    #Return values
    return categoryWords[bestValues][0], bestValues, found

def getGuess(guessed = []):
    while True:
        guess = input("Enter Your Guess or ('loss'/'win'): ")
        if (len(guess) == 1 and guess[0].isalpha() and not guess in guessed)\
        or guess == "win" or guess == "loss":
            return guess
        print("Not a valid character guess")

def getCurStatus(letters = {}, length = 0):
    word = list("_" * length)
    guessedLetters = "[ "
    if len(letters) > 0:
        for key, value in letters.items():
            if len(value) == 0:
                guessedLetters = guessedLetters + key + " "
            else:
                for index in value:
                    word[index] = key
    result = ""
    for item in word:
        result = result + item + " "
    result = guessedLetters + "] \n \n" + result
    return result[:len(result) - 1]
    
def runGame():
    fileName = 'dictionary.txt'
    words, posVals, length = getWords(fileName)   
    guesses = getGuesses()
    misses = 0
    showWords = getYN("See the total possible words 'yes'/'no': ")
    guessedLetters = {}
    #Loop until win or loss
    while True:
        
        print("You have {} guesses remaining".format(guesses - misses))
        if showWords:
            print("There are {} possible words".format(len(words)))
        #Show the current status of their guesses 
        curStatus = getCurStatus(guessedLetters, length)
        print("\n" + curStatus + "\n")
        #Get Guess
        guess = getGuess(guessedLetters.keys())
        if guess == "loss":
            print("YOU HAVE LOST. LOSER. \nThe word was", words[randint(0, len(words) - 1)])
            return [0, len(guessedLetters), guesses, length, misses]
        if guess == "win":
            print("YOU HAVE WON. \nThe word was", words[randint(0, len(words) - 1)])
            return [1, len(guessedLetters), guesses, length, misses]
        #evaluate guess and get resuld
        words, usedVals, found = findBestWords(words, posVals, guess)
        #Remove Guesses
        for val in usedVals:
            posVals.remove(val)
        #Deal with guess logic
        if not found:
            misses = misses + 1
            guessedLetters[guess] = []
        else:
            guessedLetters[guess] = usedVals
        #Check for win or loss
        if len(posVals) == 0:
            curStatus = getCurStatus(guessedLetters, length)
            print("\n" + curStatus + "\n")
            print("YOU HAVE WON. CONGRATULATIONS")
            return [1, len(guessedLetters), guesses, length, misses]
        elif guesses - misses == 0:
            print("YOU HAVE LOST. LOSER. \nThe word was", words[randint(0, len(words) - 1)])
            return [0, len(guessedLetters), guesses, length, misses]

def displayData(d = {}):
    #Create pandas dataframe for analysis
    df = pd.DataFrame(data=d)
    #Create pyplot elements
    fig, axs = plt.subplots(3)
    #Format the figure that contains the plots
    fig.suptitle('Game Data Analysis')
    fig.set_figheight(20)
    fig.set_figwidth(8)
    #Cereate bar graph of wins and losses in first subplot
    wins = functools.reduce(lambda x, y: x + y, df["win/loss"])
    losses = len(df) - wins
    axs[0].bar(['wins', 'losses'], [wins, losses], alpha=.8, color=("green", "red"))
    axs[0].set_title("Wins vs Losses")
    #Create two overlapping bar graphs for second suplot
    axs[1].bar(list(range(len(df['win/loss']))), df['guessesAllowed'], alpha=.8, color="yellow")
    axs[1].bar(list(range(len(df['win/loss']))), df['misses'], alpha=.8, color="red")
    axs[1].legend(["Guesses Allowed", "Misses"])
    axs[1].set_title("Guesses Allowed vs Misses")
    #Create three overlapping linegraphs in third subplot
    correctGuesses = []
    for i in range(len(df["guessesUsed"])):
        correctGuesses.append(df["guessesUsed"][i] - df["misses"][i])
    
    axs[2].plot(df['wordLength'])
    axs[2].plot(df['guessesAllowed'], color="yellow")
    axs[2].plot(df['misses'], color="purple")
    axs[2].plot(correctGuesses, color="green")
    axs[2].legend(["Word Length", "Guesses Allowed", "Misses", "Correct Guesses"])
    axs[2].set_title("Word Length, Guesses Allowed, Misses, Correct Guesses")


def startGame():
    #Opening Statement
    print("Hi, Welcome to Stephen's hangman app. \n\
This app allows you to play as many games of hangman as you want. \
When you finish a game it will ask if you want to play again. \
If you select no, you will have the option to see some graphs about your games.\n\
It takes at least 3 games!!! for the game to show you the graphs. \n\
If you want to skip to the graphs, use the win/loss option to simulate finishing at least 3 games.\n")
    #Dictionary to store data about games
    d = {'win/loss': [], 'guessesUsed': [], 'guessesAllowed': [], 'wordLength': [], 'misses': []}
    message = "Would you like to play hangman? 'yes'/'no': "
    #Main loop of game
    while getYN(message):
        message = "Would you like to play hangman again? 'yes'/'no': "
        #Runs the game
        game = runGame()
        #appends results of game to dictionary
        d['win/loss'].append(game[0]) 
        d['guessesUsed'].append(game[1])
        d['guessesAllowed'].append(game[2])
        d['wordLength'].append(game[3])
        d['misses'].append(game[4])
        #Calculates the fins functionally
        wins = functools.reduce(lambda x, y: x + y, d["win/loss"])
        games = len(d['win/loss'])
        #Print win Percentage
        print("\nYou have played {} game(s) and won {} of them".format(games, wins))
        print('That is a {0:.2f}% win percentage'.format((wins / games * 100)))
    #Check if theres enough data for visualization
    if len(d['win/loss']) > 2 and getYN("Would you like to see data about your games? 'yes'/'no': "):
        displayData(d)  
    elif getYN("You don't have enough data to get meaningful graphs of your own \n\
Would you like to see graphs from premade data? 'yes'/'no': "): 
        d2 = {'win/loss': [1, 0, 1, 1, 0], 'guessesUsed': [12, 5, 15, 12, 9], \
             'guessesAllowed': [10, 3, 10, 15, 7], 'wordLength': [5, 3, 7, 2, 4], 'misses': [7, 3, 8, 10, 7]}
        displayData(d2)
        

startGame()
    























