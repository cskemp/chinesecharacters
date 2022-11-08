# This script converts the raw experimental data into the cleaned files that appear in experiment/data. The raw data aren't included in this repository so it's not possible to actually run this script -- but it's included to document the processing pipeline.

# Use tidyverse
library(dplyr)
library(tidyverse)
library(here)

d <- read.csv(here("experiments", "data", "raw_data", "results_exp_pictographic_ratings_oracle_printedtraditional.csv")) %>%
  pull("content") %>%                                   # retain only the content vector
  as.character() %>%
  stringi::stri_remove_empty() %>%                      # in case we have an empty entry
  map(read_csv, col_types = cols(.default = "c")) %>%   # map each element to a tibble
  reduce(bind_rows) %>%                                 # take the list of tibbles and collapse to one tibble
  mutate(rownum = row_number()) %>%
  mutate(imgpair= str_extract_all(stimulus, "(?<=img/).+?(?=.png)")) %>%
  mutate(imgpair= map(imgpair, toString)) %>%
  separate(imgpair, c("left", "right"), sep=",") %>%
  select(turkcode, left, right, button_pressed, trial_type, responses, rownum, endperiod) %>%
  group_by(turkcode) %>%
  mutate(participantid = cur_group_id()) %>%
  ungroup() %>%
  select(-turkcode) %>%
  filter(! is.na(right) | ! is.na(responses) ) %>%
  separate(left, c("character", "leftver", "c1", "c2", "cleftver"), sep="_", extra = "merge", remove=FALSE) %>%
  separate(right, c(NA, "rightver", NA, NA, "crightver"), sep="_", extra = "merge", remove=FALSE) %>%
  unite(cc, c(c1, c2), remove=FALSE) %>%
  mutate(character = if_else(is.na(c1), character, paste("control", cc, sep="_"))) %>%
  mutate(leftver = if_else(is.na(c1), leftver, cleftver)) %>%
  mutate(rightver = if_else(is.na(c1), rightver, crightver)) %>%
  select(-cc, -c1, -c2, -cleftver, -crightver, -left, -right)

responses <- d %>%
  filter(trial_type =="survey-text" & responses != '{"Q0":""}') %>%
  select(responses)

print(responses$responses)

responses %>% write_csv(here("experiments", "data", "commentsplaceholder.csv"))


ratings <- d %>%
  filter(!(is.na(character)) & character != "NA") %>%
  select(-trial_type, -responses) %>%
  group_by(participantid) %>%
  mutate(trialnum = rank(rownum)) %>%
  ungroup() %>%
  rename(rating=button_pressed) %>%
  rename(condition=endperiod) %>%
  arrange(participantid, trialnum) %>%
  mutate(rating = if_else(leftver != "oracle", 5 - as.numeric(rating), as.numeric(rating))) %>%
  mutate(flip = if_else(leftver != "oracle", "flip", "noflip")) %>%
  select(-leftver, -rightver) %>%
  mutate( controlcorrect = if_else( str_detect(character, "^control_") & rating >= 3, 1, 0) ) %>%
  group_by(participantid) %>%
  mutate(controlscore = sum(controlcorrect) ) %>%
  ungroup() %>%
  select(participantid, condition, trialnum, character, rating, flip, controlscore, -controlcorrect, -rownum)


ratings %>% write_csv(here("experiments", "data", "placeholder.csv"))
