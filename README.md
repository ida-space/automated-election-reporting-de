# wahlbot

wahlbot automates the election reporting by generating articles based on election data.

This repo is a modified - but structurally equivalent - version of the code we used for reporting the state results on constituency and municipality level during the state election in Sachsen-Anhalt in June 2020. [This text](https://www.mdr.de/nachrichten/sachsen-anhalt/landtagswahl/warum-wir-automatisierte-wahlberichte-fuer-gemeinden-und-wahlkreise-anbieten-100.html) gives an overview of our motivation and approach.

**! Caution !**  This repo uses randomly generated sample data which does not reflect any election results.

The final articles are in German and some grammar rules are highly adapted to the election context.



The main components of the script are:

- the **article structure** - determines the final structure of an article. It can contain fixed text, as well as text modules.
  In this repo two example structures are included:
  - ```templates/preelection.txt``` for an article before the election started
  - ```templates/article.txt``` for the counting and final election results
- the **text modules** - contains the actual text with variables, e.g. ```The winning party is the *${winner}".```
  Also, the required processing steps to ensure the grammatical correctness of the text snippet is listed.
  An example is noted in ```templates/text_modules/counting.yaml```
- the **data** - is the basis for the extraction of all relevant election metrics such as the turnout, the party with the highest percentage of list share, the name of the winning candidate, etc. The information is extracted, assessed and stored as parameters which are used in the text modules. Besides the actual election results there is background information on the candidates or special information about a constituency. This information is researched and verified by editorial staff before the election. 
  This repo contains randomly generated sample data including fictional candidates from the Star Trek universe. The data is stored in ```data/```

These three components ensure a certain flexibilty. By combining certain article structures with different text modules, it allows us to easily generate articles at different stages of an election: from the preelection phase over the counting stage up to the preliminary and final results.



## Setup 

This code requires ``` python3.9 ```. If it is installed it's easy to setup a virtual environment and install all dependencies by running:

```
./run install
```



## Generating texts

The main script is called *script.py*. It generates an article for each consituency listed in the sample data files which can be found in the */data/sample/* folder.
Start the script with:

```
./run run
```

A possible flag is *--init* or *-i*. It initializes the articles with the preelection text. By default it is set to false.
```
./run run --init
```

A results folder containing a ```txt``` file for each consituency is created.



## Detailed Process

1. sample data is loaded from *./data/sample/*

2. previous progress state for each region is loaded. e.g. previous progress state: 5 districts are counted
   current progress is loaded and stored as csv in ```./src/data/progess_....csv``` for the next iteration
   
3. If not state results are present, the entire script is stopped!

4. results on state level are computed, e.g. winning party, turnout, 

5. For each constituency:
   1. If the constituency is on the blacklist, the next steps are skipped and for this region no article is created
   2. If all data in this constituency is None, the next steps are skipped and for this region no article is created
   3. a status is set: ```init``` ```counting``` or ```final```
   4. current progress is determined, e.g. 7 districts are counted
      if previous progress == current progress, the next steps are skipped as the article with this progress state already exists
   5. cleanup data: remove results for party "Sonstige" as well as all information for any row in which the column with percentage of votes (*in %*) is None, as this party might not be represented in a specific municipality
   6. process election results to get all required parameter (e.g. winning party, turnout, number of invalid votes)
      On constituency level the results are computed for direct share (Erststimmen) and list share (Zweitstimmen). The corresponding parameter contain respectively the prefix ```list_``` or ```direct_```
   7. parameter are assessed such that specific text modules change dependent on the election outcome (e.g. if the difference to a previous election is positive it's a "win" while if it is negative it's a "lost".)
   8. parameters are formatted:
      - numbers are converted to strings containing a comma instead of a point to indicate decimals, e.g. ```14.5 --> "14,5"```
      - for numbers with *,0* the decimals are removed, e.g. ```16,0 -> 16```
      - integer between 0 and 12 are changed into written numbers, e.g.``` 4 --> vier, 9 --> neun ``` 
   9. Based on the status the respective article structure, e.g. ```article.txt``` or ```preelection.txt``` in ```./src/templates/``` and text modules, e.g. ```counting.yaml, final.yaml``` in ```./src/templates/text_modules/``` are loaded
   10. For each text module the corresponding apply the specified postprocessing steps. This could be:
      - gender: switch the gender of a sentence
        e.g. ```XY, Direktkandidat der Linken --> XY, Direktkandidatin der Linken```
      - pluralize party name
        e.g. ```Die Grüne führen --> Die Grünen führen```
      - pluralize verb dependen on party
        e.g. ```Linke kommt auf Platz 2 --> Linke kommen auf Platz 2```
      - singularize word after 1
        e.g. ```ein Verlust von einen Prozentpunkte --> ein Verlust von einem Prozentpunkt```

   11. A validity check is performed: e.g. the teaser length is checked to not exceed a certain number of characters or it is checked whether the winning direct candidate is listed. Only if all checks are passed the next step is executed
   12. article is saved in ```./results/```









