from flask import Flask, request, render_template
import math
from indicnlp.tokenize import indic_tokenize
from nltk.tokenize import word_tokenize
from googlesearch import search
from langdetect import detect
import nltk

nltk.download('punkt')

app = Flask("__name__")

@app.route("/")
def loadPage():
    return render_template('index.html', query="")

@app.route("/", methods=['POST'])
def cosineSimilarity():
    try:
        universalSetOfUniqueWords = []
        matchPercentage = 0
        plagiarizedSources = {}

        inputQuery = request.form['query']

        # Detect language of the query
        query_language = detect(inputQuery)

        # Tokenize the query based on language
        if query_language == 'hi':
            queryWordList = indic_tokenize.trivial_tokenize(inputQuery)
        else:
            queryWordList = word_tokenize(inputQuery)

        for word in queryWordList:
            if word not in universalSetOfUniqueWords:
                universalSetOfUniqueWords.append(word)

        with open("database1.txt", "r", encoding='utf-8') as fd:
            database1 = fd.read().lower()

        # Tokenize the database text
        databaseWordList = indic_tokenize.trivial_tokenize(database1)

        for word in databaseWordList:
            if word not in universalSetOfUniqueWords:
                universalSetOfUniqueWords.append(word)

        queryTF = []
        databaseTF = []

        for word in universalSetOfUniqueWords:
            queryTfCounter = 0
            databaseTfCounter = 0

            for word2 in queryWordList:
                if word == word2:
                    queryTfCounter += 1
            queryTF.append(queryTfCounter)

            for word2 in databaseWordList:
                if word == word2:
                    databaseTfCounter += 1
            databaseTF.append(databaseTfCounter)

        dotProduct = 0
        for i in range(len(queryTF)):
            dotProduct += queryTF[i] * databaseTF[i]

        queryVectorMagnitude = math.sqrt(sum(tf ** 2 for tf in queryTF))

        databaseVectorMagnitude = 0
        for i in range(len(databaseTF)):
            databaseVectorMagnitude += databaseTF[i] ** 2
        databaseVectorMagnitude = math.sqrt(databaseVectorMagnitude)

        matchPercentage = (dotProduct / (queryVectorMagnitude * databaseVectorMagnitude)) * 100

        if matchPercentage > 0:
            # Perform web search to identify plagiarized sources
            urls = get_search_results(inputQuery, query_language)
            for word in queryWordList:
                for url in urls:
                    if word in url and word not in plagiarizedSources:
                        plagiarizedSources[word] = url

        output = "Input query text matches %0.02f%% with the database." % matchPercentage
        sources = "The text is plagiarized from the following sources:<br>"
        for word, url in plagiarizedSources.items():
            sources += f"<b>{word}</b>: {url}<br>"

        return render_template('index.html', query=inputQuery, output=output, sources=sources)
    except Exception as e:
        print(e) 


        output = "Please Enter Valid Data"
        return render_template('index.html', query="", output=output)

@app.route("/about")
def aboutpage():
    return render_template('about.html')



def get_search_results(query, language):
    # Use the search function to perform a web search
    # Modify the parameters as per your requirement
    search_results = search(query, num_results=5, lang=language)

    # Extract the URLs from the search results
    urls = []
    for result in search_results:
        urls.append(result)

    # Return the list of URLs
    return urls


if __name__ == '__main__':
    app.run()

