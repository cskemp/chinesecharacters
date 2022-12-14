Materials for the shiny app available at

http://www.charleskemp.com/code/chinese_complexity_change.html


#### images_full
contains images for all characters in the CLD. The app doesn't use the full set because we're hosting it on shinyapps.io which currently allows up to 6000 files only


#### images
contains the images used by the app. These images consist of all 232 pictographic and all 48 pictologic characters in the Chinese Lexical Database (CLD), and the 1333 most frequent characters among the remaining characters in the CLD.



#### assorted details

cld_pinyin.csv was created by copying cld_translations.csv and adding pinyin column based on 

https://www.chineseconverter.com/en/convert/chinese-to-pinyin

I previously used the "pinyin" library in R but found it unreliable.

Manual changes to cld_pinyin.csv:

* 唔,Well, 锟?  -> 唔,Well, wú 
* 戸,household, 戸 -> 戸,household, hù 
* 嗯,Um, 锟? ->  嗯,Um, ēn 
* 嘛,Well, mB  -> 嘛,Well, ma  

