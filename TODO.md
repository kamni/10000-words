# TODOS

## 1. Load document with one sentence per line

* Sentence Adapter
  * Port
    * create_or_update
    * get_all for document
  * In Memory
    * setup.cfg
    * tests
  * Django
    * setup.cfg
    * tests
  * UI
    * setup.cfg
    * tests

* Upload adds sentences
  * Displays sentences in Edit view
  * Export button back to TOML

---

* Personal settings
  * preferred language
  * learning languages
* Add translations to sentence
* Edit translations

---

* Add DisplayText
* Adapters
  * DisplayText
    * port
      * create_or_update
        * Needs to be called when sentence is create_or_update-ed
      * get_all for sentence
    * In Memory
      * setup.cfg
      * tests
    * Django
      * setup.cfg
      * tests
    * UI
      * setup.cfg
      * tests

---

50 Repetitions for learning

* Adapters for each model:
  * Word
    * In Memory
    * Django
    * UI
  * Update Document
    * In Memory
    * Django
    * UI
* In-Memory adapters read from and write to TOML, so we keep state
  * Which file is configurable in setup.cfg
* I need a util that can be used in both in-memory and django adapters

## Where am I trying to get to?

I'm trying to work through the "Een Beetje Nederlands" episode.
This means:

1. Load a document with one sentence per line.
2. Choose which sentences I want to work with.
3. For each sentence I picked:
   * Add a translation.
   * Mark:
     * Ignored
     * Learned
     * To Learn
     * Learning will be marked automatically when I move to practice.
     * This automatically updates all words with the same base
   * Combine/change base word (doesn't auto-update other words,
     but the combination will be given as a suggestion when updating).
   * Add additional sentence examples + translations
     for "To Learn" words
   * See the document progress of Learned + Ignored
4. Practice:
   * Select by:
     * language (all documents for language will be practiced)
     * document (only sentences for the document will be studied)
   * Dutch to English unscramble
   * English to Dutch unscramble
   * Hear Dutch sentence and unscramble
   * Hear Dutch sentence and free-form type
   * Punctuation is not counted in correctness
   * Each exercise is shown 5 times before progressing to next
     (scattered with other exercises)
     * When free-form typing is mastered,
       brings in another sentence to mark up?
     * Brings back old sentences on a timed schedule, free-form type
5. See progress on each document for learning.
6. Export to TOML for re-upload.

---

## Unfinished:

* finish edit01 prototype
  * delete scripts/prototype_deleteme.py
* finish practice01 prototype
* Add validation to EditView upload
  * tests

---

## Refactor with Controllers

* Tests for existing EditView

* We have logging on everything?

---

## EditO1 Prototype

* Sentence widget
  * Add a translation
* Batch change words in a sentence


## ObservableDict

ObservableDict app.storage.client can add handlers with `on_change`
events.handle_event(handler, events.ObservableChangeEventArguments(sender=self))

Could we make documents/sentences/words observable dicts?


## Import steps

1. Import a text with single lines.
2. Add a translation of the sentence.
3. Mark up the sentence (and mark up other sentences automatically).
   * For individual display text, change the underlying word
     * Bulk change...how can I make this less painful?
4. For learning/to-learn sentences, upload example sentences.
5. Export document as TOML

* We'll worry about combo words later.

## Sentences: Prototype

* Create models
* Create adapters
  * In Memory
    * tests
  * Django
    * tests
* Store document
  * In Memory
    * tests
  * Django
    * tests
* Generate test data that can be loaded
  * Script to load data
* Update the frontend to use models

---

* Combining words
  * Combine words menu item needs black text

  * Covert everything to actual pydantic models,
    so I'm not getting confused about index versus attribute
  * BUG: second time we try to combine a word doesn't work
  * BUG: Setting status on combined word doesn't work

  * We need to replace labels if they're consecutive
  * Refreshable sentence?

  * Change the word associated with display_text
  * how to handle in sentences when they're separate?
    * color really needs to change based on word
    * get display text from marker?
    * reorder display_text by ordering
    * create new word, or get existing
    * create new label with word's marker
    * if they're consecutive, we can merge them
    * see if any are consecutive; they can merge
    * it points to the same word
      * I need a word lookup
    * sentence should refresh
  * Replacing in the rest of the document

* Model to approve/edit combined words

* Spinner while loading

* Clean up prototype
  * CSS:
    * Can add sass, scss
  * Models?

---

## Senentences: File Upload and Translations Prototype

* Upload translations (later or at the same time)
* Tabs per language?
* Manually add translation

---

* set default classes
* Tabbed view for translations

* Switch to toml / tomllib
  * tomllib.load(opened_file)

* Uploading translations at the same time

* Put some explanatory text about word color in the right sidebar
* Words in document learned as percentage
* Put multiple into the same word (orange) -- ctl click?

* Sentences are displayed as individual words, color-coded by status
  * white background, black text: ignored or learned
  * gray background, black text: not set
  * learning: light green background, black text
  * waiting to learn: lavendar background, black text

* Nice to have:
  * Loading icon until document loads
  * Cleanup: don't display extra classes...

---

## Documents

* Nicegui: upload a document
  * Form validation
    * input has validators...figure out how
  * Warning if file already exists, and confirmation dialog
  * How do I clear the input forms?
  * In-Memory Adapter
    * needs to handle file upload
  * Tests:
    * Document Adapter
    * In-Memory Adapter

---

* Nicegui: Upload a document file, split into sentences
  * I don't really have to save the file, do I?

* Disable buttons like 'Save' to prevent double-clicks
* Settings where you can choose your languages, to make the dropdown easier
  for upload

---

* Adapters: db to ui, so we only have one to import to the frontend?
* Run frontend tests with both django and in-memory?

* Scripts
  * tests for load_data
  * tests for create_test_data

* AppStore: should I make the other stores not singletons?

* Get permission to use fairy tales
  * If not permission, remove and update README

---

## Cleanup

* coverage
* lint
* mypy
* copyright checker
* poetry?
* Figure out config format -- all TOML?
  * Separate out my config by type? (e.g., dev vs prod)

---

## Exception handling

* app.on_exception

---

## Document

* Split document into sentences
    * Sentences are the same when they match without punctuation
    * How to store punctuation?
* When storing sentences, close quotation marks.
* Click on sentence to add translation
* After adding a translation, words become individual labels
* Left-clicking on word plays Google TTS
* Right-clicking a word sets status
* Ctrl-left-click allows multiple to be selected for phrase
* Upload a translation document to automate
  * Set primary language, don't show docs for that language in the sidebar
    * Show them as a list of translations

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
   4. gray background, black text: Unknown type.
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
