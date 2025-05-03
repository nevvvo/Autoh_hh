**The algorithm of operation**
The script opens a link from the list of available ones. Then he starts checking all vacancies, excluding those that do not meet the specified criteria. The excluded_words list is used for this purpose.
Upon completion of the verification of all links, the script saves all vacancies in a variable and waits for user authorization.
After user authorization, the script performs the following actions for each vacancy:
1. Clicks on the link.
2. Presses the "Reply" button.
3. Checks if there is a text input field.
    * If the field is present, the script will attach a cover letter.
    * If there is no field, it sends a response without text.
4. Moves on to the next vacancy.
