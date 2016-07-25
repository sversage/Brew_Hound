# Brew_Hound
Application to recommend micro breweries to a user based upon their current geographical location and prior tastes.

# Project's Motivation:

While travelling, moving to a new city it's difficult to point establishments which would cater to an individual's tastse by a simple google search. As such, I wanted to create an engine that would allow for an individual to input their favorite adult beverage and a desired location and to be able to recommend MicroBreweries near by along with which beverage(s) they may enjoy at the venue. 

# Data Exploration

Once the data was scraped from the internet and parsed from MongoDB into PSQL, I created the two visuals below to get a sense of what information was available for the analsys. 

Heat Map by state:

![ScreenShot](https://github.com/sversage/Brew_Hound/blob/master/webapp/screen_prints/Screen%20Shot%202016-07-25%20at%204.21.50%20PM.png)

Relative City Count: 

![ScreenShot](https://github.com/sversage/Brew_Hound/blob/master/webapp/screen_prints/Screen%20Shot%202016-07-25%20at%204.22.02%20PM.png)

# Recommendation system

The recommender system is a content based filtering engine, similar to the model Pandora uses for their song selection. The user inputs their favorites beers and desired location, at which point the app will calculate cosine similarity and return the most similar beers as recommendations. Some of the features used in the similarity calculation include ABB, SRM, IBU, category and style. 

Webapp URL: https://brew-hound-app.herokuapp.com/

# Next steps

I intend on creating functionality to allow users to rate the recommended beers so that once enough reviews are collected NMF could be leveraged for recommendations and the cosine similarity will be used for new users to address the cold start problem. 

#Scripts Included

Within the Repo there are scripts to facilitate collection of the data via API into a MongoDB, parsing the relevant information from Mongo into Postgres, feature engineering, and building a content filtering recommendation engine based upon a users tastes and location. 

Moreover, there are scripts within the repo to run a REST API. 

#APIs Leverage

I would like to say thank you to BreweryDB and BreweryMapping for allowing me to use their API in making this app possible. 
