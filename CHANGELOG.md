CHANGELOG

# Alpha

## 0.1.0a:
### 2 July 2022

- Initial Release.

## 0.1.1a:
### 12 July 2022

- Updated URL verification regex. 
- Fixed url regex matching bugs. 
- Implement type hinting in source code.
- Refactor `allpress.web.Crawler().create_url_tree()` function as `index_site()`
- Add keyword argument `num_to_index` to `index_site()` function to allow crawler to stop indexing once it has found a predefined number of pages.

## 0.1.2a:
### 16 July 2022

- Updated URL verification regex.
- Fixed URL regex matching bugs.
- Implemented BeautifulSoup library, cleaned up code.
- Begin work on database implementation (psycopg2)

## 0.2.0a


- Added modules `settings.py` and `lexical.py`.
- Implemented some lexical processing;
- Ability to detect language of strings of text, relies
on `googletrans` library.
- Ability to compile web page `<p>` tags into one body of text.

## 0.3.0a
### 1 August 2022

- Continue implementation of postgres data models.
- Begin implementation of migration features.
- Moved `URL_REGEX` and `HREF_PARSE_REGEX` to `settings.py`

## 0.4.0a


- Add database migration features for `PageModel`.

## 0.4.1a
### 2 August 2022

- Remove lambda functions for generating insertion queries and table creation queries.
- Refactored code to better follow PEP.
- Added method to create database model for translation objects.
- Refactored code and relocated some functions

## 0.4.2a
### 4 August 2022

- Add primary key constraint for `pg_page` table in PostgreSQL database.

## 0.4.3a

- Add documentation.

## 0.5.0a
### 5 August 2022

- Over haul `allpress.db.cursor` transaction system.
- Make `allpress.web.Crawler().index_site()` method recursive.

## 0.5.1a

- Complete method to provide for migration of `TranslationModel`.

## 0.6.0a
### 13 August 2022


- **Major update**
- Major refactoring of package structure.
- Add new database models, `StateModel` for individual countries, and `NewsSourceModel` for individual news sources.
- Begin adding API methods for allpress, specifically `allpress.add_country_to_db()`, `allpress.add_all_countries_to_db()`, and `allpress.create_crawler`
- Begin working on lexical analysis for search querying.
- Add requirements.txt

## 0.6.1a
### 15 August 2022

- Add new functions to the API, `select_news_source()` and `select_page()`. Allows you to query against the DB for specific news sources.

## 0.6.2a
### 22 August 2022

- Add `geo` module to allpress
- Contains `Coordinate`, `Region` classes to help define areas of search queries

## 0.6.3a
### 5 November 2022

- Create test cases.
- Improvements to the geolocation module.

## 0.6.4a
### 8 November 2022

- Optimize `allpress.models.create_country_model()` function.
- Fix bugs with page querying code.

## 0.7.0a
### 24 November 2022

**Major Update**
- Add catalog index of scraped webpage urls, for search querying. Language gnostic. 
- Major overhaul of web Crawler scraper code, now utilizes multithreading, is several times faster.
- Refactor package for cleaner organization
- `request_manager.RequestPoolManager` class to manage handling of rate limiting and multithreading of
http requests.
- `pg_translation` is no longer a single table for storing all translated versions of articles. It now discriminates based on language. This is done to make it possible for `tsquery()` in the database to be done across multiple languages.
- Add SQL code to generate English and Spanish search columns in their respective `pg_translation` tables to allow `tsquery()` to be executed.

## 0.7.1a
### 26 November 2022

- Updates to web crawler, database insertion function to make web crawling more accurate
- Updated URL verification regex.
- Fixed URL regex matching bugs.

## 0.7.2a
### 29 November 2022

- Implement rudimentary full text SQL searches through the `allpress.search_by_text()` method.
- class `io.Indexer` has been removed.
- module `allpress.db.io` has been refactored to `allpress.db.query`

## 0.7.3a
### 17 December 2022

- Complete documentation for non private functions.
- Change license to GPL v3.

## 0.7.4a
### 17 December 2022    

- Add tsquery support for Arabic, Armenian, Basque, French, Hindi, Italian, Portuguese, Russian, and Spanish.
- Multilingual support for search queries. Can automatically detect language of the search query. Returns results
in a list.

## 0.7.5a
### 17 February 2023

- Edit `pg_page` table in database, to add column for date of webpage. To be used to assist with search relevancy in the future.