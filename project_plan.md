# Project Plan
## Week 1 (April 25 - May 1): Assemble dataset, validate that there’s a pattern, green-light decision
### Background reading (Malika)
- Start final report jupyter notebook (deepnote)
- General bioacoustics projects
- Bioacoustics as marker of environmental stressors
- Quality control - how data gets into xenocanto / cornell
- More research questions that involve soundscape or weather data
### Set up data processing (Adithya)
- Set up DVC, readme
- Getting environmental recordings from xenocanto + Cornell
- Find if there’s one location that has enough recordings over time
    - Normalize by human population (indicates how urban it is)
    - Normalize by time of day
- Pull weather data from OpenWeather API for each environmental recording

### Data exploration / validate pattern
- Listen for patterns, looking at recordings with nominal vs extreme weather/pollution

### Decision time (Thurs)
- Decide if we’re sticking with this idea, or switch to another option
    - Air pollution based on traffic
    - Bird song clustering (based on experimentswithgoogle)
    - Predict bird activity based on pollution (Kolter thought this might be easier?)

## Week 2 (May 2 - May 8): Audio feature extraction, ML
### Audio feature extraction
Extract MFCC, spectrograms

### ML
- Deep learning to extract features from spectrograms OR manually select audio features
Supervised linear regression model, trying different weather metrics as prediction

## Week 3: Documentation + Overflow
### More work on ML
### Evaluate correlation (Adithya)
- Ablation analysis to ensure soundscape features are significant in the prediction
- Some kind of statistical evaluation to ensure there’s actually a correlation

### Video (max 90s) - May 14 (Malika)
- Animation / visualization
- Voiceover

### Final Report - May 17
- Background
- Problem statement / question
- Data used
- How the data can be used to draw conclusions
- What we did
  - Featurization
  - ML analysis
  - Evaluation
- Reflection / Future work
