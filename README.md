Generate recommendations for any one of your spotify playlists!

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<p align="center">

  <h3 align="center">spotify recommendation system</h3>

  <p align="center">
    Let Stats find you some tracks!!
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#Methodology">Methodology</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

The aim of this project is to generate song recommendations for a target spotify playlist given a source playlist.

### Built With

This section list major frameworks that is used to built the project.
* [Python](https://www.python.org)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Spotipy](https://flask.palletsprojects.com/en/1.1.x/)

### Methodology
![process][methodology-0]

Each song in the source playlist is represented as a vector in the feature space. 

Our feature space consists of 3 major type of song features:

1. Genre that the song belongs to.( We used TFIDF to encode the genre )
2. Audio Features of the song. ( As provided by spotify )
3. Descriptive features of the song which were engineered.

Once we have vector of every song in our source playlist, we summarize all the songs to generate a single vector.
![sum][methodology-3]

![cosine sim][methodology-1]

We search for a song vectors in our target playlist, which are most similar to our source playlist vector.

#### TF-IDF
In information retrieval, tf–idf, TF*IDF, or TFIDF, short for term frequency–inverse document frequency, is a numerical statistic that is intended to reflect how important a word is to a document in a collection or corpus.[1] It is often used as a weighting factor in searches of information retrieval, text mining, and user modeling.

![tf-idf][methodology-2]


<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

You will need to setup a spotify [developers account](https://developer.spotify.com) and create an app over there. Once you are done with that, you will receive a CLIENT_ID and CLIENT_SECRET which will help you to pull data from spotify account. 

In server.py file replace fill these feilds as displayed in your app 
```
client_id = '2ab55afd64cd4a9a86bb74e93a4f75f5'
client_secret = '20d4708024db41d6a193b4d03e08d55e'
```
You will also need to edit seeting on your dashboard and fill out redirect URI field in the Edit Settings section.
![app setting][setting-screenshot]

This redirect URI shoild be same as in util.prompt_for_user_token
```
util.prompt_for_user_token(scope, client_id=client_id, client_secret=client_secret,
                                   redirect_uri='http://google.com/')
```

<!-- USAGE EXAMPLES -->
## Usage

The first step will be to start the flask server. Follow these steps:

1. cd to server folder.
2. use 
```
python util.py (your spotify user URI)
```
for example my user URI is : spotify:user:7ur7jjowtivgnatopjff8102l

```
python util.py 7ur7jjowtivgnatopjff8102l
```
You can access playlist URI like this
![Alt Text](https://media.giphy.com/media/rEq1P8mItXXtMGqJ1W/giphy.gif)

You can launch the app in the browser using client/index.html file. Once you launch the app in the browser the source playlist URI goes in the left text field and the target playlist URI goes in right text field. Hit **search**


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Img Shields](https://shields.io)
* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Pages](https://pages.github.com)
* [Animate.css](https://daneden.github.io/animate.css)
* [Loaders.css](https://connoratherton.com/loaders)
* [Slick Carousel](https://kenwheeler.github.io/slick)
* [Smooth Scroll](https://github.com/cferdinandi/smooth-scroll)
* [Sticky Kit](http://leafo.net/sticky-kit)
* [JVectorMap](http://jvectormap.com)
* [Font Awesome](https://fontawesome.com)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: images/product.png
[setting-screenshot]: images/app_setting.png
[methodology-1]: images/cosine_sim_2.png
[methodology-0]: images/process_2.png
[methodology-2]: images/tfidf_4.png
[methodology-3]: images/summarization_2.png


Useful resources:
1. My YT video describing the process: https://www.youtube.com/watch?v=tooddaC14q4
2. Kaggle Data: https://www.kaggle.com/yamaerenay/spotify-dataset-19212020-160k-tracks
3. Spotipy Documentation: https://spotipy.readthedocs.io/en/2.16.1/
