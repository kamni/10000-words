# TODOS

## Cleanup

* coverage
* lint
* mypy
* copyright checker

---

## Exception handling

* app.on_exception

## Document

* Document model should use the uuid of UserSettings
  * Django
  * Pydantic -- id only
* Document port/adapter
  * Add adapters to config
  * Create models
  * Write ports
  * Write tests
  * Upload includes a force override to upload to same document name
* Nicegui: if no documents, suggest an upload
* Nicegui: Upload a document file, split into sentences
* Nicegui: display uploaded document by language in sidebar
* Nicegui: can see document by clicking on it
* Nicegui: Can upload same document twice, with warning dialog;
  overwrites existing document

---

## Document

* Click on sentence to add translation
* After adding a translation, words become individual labels
* Left-clicking on word plays Google TTS
* Right-clicking a word sets status
* Ctrl-left-click allows multiple to be selected for phrase
* Upload a translation document to automate

---

## Logging

* Log when user is created (username, admin status)
* Log when user logs in (username, admin status)
* Log when a document is uploaded

---

## Thoughts

Here's the flow that I'm thinking of:

Editing Mode:

1. Upload a file.
   1. The script creates a new, Unknown word for each word, unless the word
      already exists.
   2. If the word already exists, append the sentence to the word (if the
      sentence doesn't already exist.
   3. Pull down the audio file from gTTS for each sentence (max characters
      is 100, so may have multiple files)
2. You're taken to a reading file.
   1. Sentences are in light gray, black text.
   2. Click on the sentence to bring up an edit modal.
   3. The edit modal allows you to add one or more translations.
      Translations are a string pared with a known language code
3. You're taken back to the reading file. Words translated show up in colored
   backgrounds to indicate their status:
   1. white background, black text: learned
   2. lavender background, black text: learning
   3. light green background, black text: defined, but not added to learning
      rotation.
   4. orange background, black text: Unknown type.
4. You handle all Unknown words. Left-click to bring up an editing modal:
   1. Set the type -- multiple words are type "Expression" -- ctrl+click to
      select multiple.
   2. Add translations.
   3. When saved, backend gets gtts translations for all words.
   4. You will be able to play each individual word.
5. Back in the reading file, you can right-click words to change their status
   to 'learned' or 'start learning'. You can also change any known words to
   one of the others. Left click to bring up the edit page again.

Learning mode:

1. Iterate through words set for learning.
   1. Ordering based on when last seen -- interval method.
   2. Can set how many words to study per day.
2. Sentence practicing:
   1. See/hear foreign text, rearrange bubble words in primary language
   2. See/hear primary language text, rearrange bubble words in foreign language.
   3. Hear foreign text, type what you heard.
   4. Option to turn off seeing text in #1 and #2

Score for number of words you've learned

Store word -- are all of them user-related? No uneditable words?
Selected translations?
You are responsible for your own copyright

## Database Models

* Language Code
  * code (unique)
  * display name

* Document
  * File
  * Display name
  * User who uploaded (unique with file and language code)
  * Language code
  * Sentence[] - Many to Many; must match language code

* Sentence:
  * Document - Many to Many; must match language code
  * Ordering within document
  * User who uploaded (unique with ordering, text, and document)
  * Language code
  * Text
  * Words[] -- Many to Many; must match language code
  * Translations[] - Sentence[]; many to many

* Word
  * Language code - unique on language code + text
  * Text
  * User who uploaded (unique with language code and text)
  * Sentence[] -- Many to Many; must match language code
  * Translations[] - Word[]; many to many
  * See other properties in the Word model file
