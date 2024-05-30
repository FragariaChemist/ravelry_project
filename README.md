# 🧶 Ravely Knitting Pattern Recommender System Using Cosine Distances and SpaCy Natural Language Processing

## Background

[Ravelry](https://www.ravelry.com/) is a social networking platform, library, and organizational tool for fiber artists.  Pattern designers can also promote and sell their patterns through Ravelry.  The website opened in 2007 and is free to use.  As of 2022, over one million patterns have been released on Ravelry.  If you are a fiber artist, chances are you have heard of Ravelry.
## Problem Statement

Ravelry has a massive pattern database and over 11 milllion users as of 2023.  Choosing a new project can be daunting for fiber artists and lead to decision fatigue.  A recommender system which suggests similar patterns based previously enjoyed patterns can make the process more enjoyable.  Fiber artists would be more willing to purchase more patterns when the process of selection isn't overwhelming.

This project attempts to create a content-based recommendation system that suggests five similar patterns to one that a user enters.  The user can click on the generated URL to go to the Ravelry pattern page for more details and download.

## Sources
* [Ravelry Reveals! 79+ Statistics, Insights, Trends, Stats For 2023](https://knitlikegranny.com/ravelry-stats/)
---
## Dataset Dictionary

|Dataset|Type|Source|Description|
|---|---|---|---|
|**(garment)_details.csv**|*various*|Ravelry API|Multiple csvs containing data collected from Ravelry API.  Separated by garment type (beanie-toque, mid-calf, etc.).
|**rav_clean.csv**|*various*|Generated|Concatenated data from garment_details csvs that has been cleaned and all nulls removed.| 
|**rav_rec.csv**|*cosine distance vectors*|Generated|Recommender database of all collected patterns.
|**rav_rec.pkl**|*pickle file*|Generated|Picked version of rav_rec.csv

## Ravelry API Sources
- [Ravelry API Documentation](https://www.ravelry.com/api)
- [Ravelry API Group](https://www.ravelry.com/groups/ravelry-api)
---
## Analysis

A total of 6000 patterns were collected from the Ravelry database.  They consist of 2000 patterns from each of the following garment types:
* Beanies & Toques
* Mid-calf Socks
* Pullovers

Ravelry stores patterns written from designers all around the world.  In an effor to not overwhelm the Ravelry API and to keep the project within scope, I chose to pull 2000 most popular patterns per garment type.  They were further filtered by knitting patterns written in English from the USA.  Discontinued patterns were excluded.

Null values were addressed as follows:
* 'gauge' values were filled based on the 'yarn_weight' feature.  Yarn weight have typical gauges which is outlined by the [Craft Yarn Council](https://www.craftyarncouncil.com/standards/yarn-weight-system).
* 'max_yardage' values were calculated based on average max_yardage values of garment/yarn_weight combination.
* 'notes' feature filled with 'notes not provided'
* 'price' feature filled with 0.  Patterns without a price can be downloaded free of charge
* 'gauge_divisor' feature filled with 4.0 as the majority of gauges on yarn are given as stitches per four inches


SpaCy was used as the natural language processor before modeling the data.
* [Text Classification using Python SpaCy](https://machinelearninggeek.com/text-classification-using-python-spacy/)
 * [SpaCy Tokens](https://spacy.io/api/token)
 * [Natural Language Processing With SpaCy in Python](https://realpython.com/natural-language-processing-spacy-python/#lemmatization)

'gauge' and 'gauge_divisor' features were used create a new feature called 'gauge_per_inch'.  This feature is a normalized gauge value which is better for the recommender system over the previous two features.

#### Feature Dictionary

|Feature|Type|Description|
|---|---|---|
|**author**|*string*|Author of knitting pattern
|**difficulty_avg**|*float*|Average difficulty determined by Ravelry users based on rating 1-5 and 5 being the most difficult.
|**max_yardage**|*float**|The maximum amount of yarn expected to be used to knit pattern if suggested yarn is used
|**notes**|*string*|Notes the designer can add to the pattern details
|**pattern_price**|*float*|Price of pattern.  Will be 0 if pattern is free
|**projects_count**|*int*|Count of projects using the pattern and logged as started by Ravelry users
|**queued_projects_count**|*int*|Count of projects using the pattern Ravelry users have added to their queues, but haven't started yet
|**ratings_avg**|*float*|Average rating Ravelry users have given the pattern based on how much they like it.  Based on 1-5 and 5 meaning a user loved the pattern.
|**yarn_weight**|*string*|Weight of suggested yarn to use for pattern
|**type**|*string*|Type of knitting pattern (hat, pullover, etc.)
|**gauge_per_inch**|*float*|Stitch per inch of pattern using suggested yarn



Code for Streamlit deployment is also included in this repository.

---

# Conclusion

I was able to successfully create a recommender system that returns five similar patterns and their Ravelry links to the user.

To test, I compared my results to Ravely's recommendation system.  Each pattern has a link on the page titled 'People who like this pattern also like...' which reccomends other patterns.

I searched for recommendations using my system and the Musselburgh hat pattern.  This pattern has a overall rating of 4.8, using fingering weight yarn, and written by Ysolda Teague.  The following results were:

|Pattern|Overall Rating|Difficulty Rating|Yarn Weight|Project Count|Project Queue|Author
|---|---|---|---|---|---|---|
|**Musselburgh**|**4.9**|**2**|**Fingering**|**23805**|**3114**|**Ysolda Teague**
|Hermione's Everyday Socks|4.7|2|Fingering|40897|13612|Erica Luedar
|Turn A Square Hat|4.5|1|Worsted|20280|7239|Jared Flood
|Monkey Socks|4.6|3|Fingering|23277|6087|Cookie A
|Simple Skyp Socks|4.7|2|Sport|11863|5596|Adrienne Ku
|Jaywalker Socks|4.3|3|Light Fingering|12389|3919|Grumperina

The only pattern in which both my and Ravelry's recommender system suggested was Hermione's Everyday Socks. This was my first recommedation and Ravelry's second.  I think this is to be expected since Ravelry has its entire pattern database at its disposal.

Next I tried a pattern I have personally knit and enjoyed called Sipila by Caitlin Hunter.  Caitlin is a prolific knit designer with dozens of patterns available on Ravelry.  This time both my and Ravelry's reccomender were quite similar, only because both systems recommended patterns designed by Caitlin Hunter.  

Finally I tried a pattern titled Brassica because the author only has three patterns published on Ravelry.  This time my recommender did not match any of the patterns that Ravelry recommended. I noticed that all of my recommendations were the same yarn weight as Brassica, but Ravelry suggested more patterns in different yarn weights.

I don't know how Ravelry structures its recommender system.  It may use or weight features differently than my system.  It seems to match nicely when the pattern is from a popular designer, but less so in other cases.  Ultimately I think this is a good started with the data I have.