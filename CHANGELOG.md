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
### 16 July 2022

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
### 1 August 2022

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
### 4 Auust 2022

- Add documentation.
