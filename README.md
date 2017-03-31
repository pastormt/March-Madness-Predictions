# March-Madness-Predictions

A Python program to predict the NCAA March Madness Basketball results based upon per team regular season data, including: 
- CBS Sports' Strength of Schedule (http://www.cbssports.com/collegebasketball/rankings/sos)
- average point differential
- ESPN Basketball Power Index (http://www.espn.com/mens-college-basketball/bpi)
- tournament seeding

Together, strength of schedule and average point different account for how well a team played against its opponenets, and how good those opponents were. 

Tournament seeding and ESPN's BPI were used as benchmarks. As a baseline, the simplest prediction system would be to use tournament seeding -- so I wanted to do better than by that method alone. On the other hand, ESPN, as a leading sports analysis organization, offers the BPI, which is "a team rating system that accounts for the final score, pace of play, site, strength of opponent and absence of key players in every Division I men's game." I was curious to see how rank and score combinations of strength of schedule and avg point differential would compare to both of these benchmarks.

ESPN BPI data was only available from 2012 to the present (at the time the experiment was done), so I predicted the tournaments from 2012 - 2015.

The Python code in "analysis.py" matches up teams based upon seeding, and predicts the winner based upon the scoring system it takes as an input argument. The code also calculates the cognitive diversity between any scoring systems given as inputs -- with greater cognitive diversity in past studies correlating with greater reward from combining systems. 

￼"analysis.py" provides a full breakdown of precision at each power of 2 from 1 to 64, however, to summarize with precision at 16 (i.e. accuracy of predicting those teams that actually wound up in the Sweet 16, averaged over the years for which the system is predicting):

+ Combining SOS and avg point differential by rank or by score yields a P@16 of 62.5%, a 12 percentage point improve￼ment from either SOS or avg point diff alone
+ Both tournament seeding (64%) and ESPN BPI (65.6%) performed slightly better (P@16) than the combination of SOS and avg point diff
+ I went into the experiment expecting ESPN's BPI to perform far better than tournament seeding. This did not turn out to be the case. 

For full results and a graphing of cognitive diversity of the various systems used, run "python analysis.py" in a terminal window
