CHANGELOG

# Alpha

## 0.1.0a:

- Initial Release.

## 0.1.1a:

- Updated URL verification regex. 
- Fixed url regex matching bugs. 
- Implement type hinting in source code.
- Refactor `allpress.web.Crawler().create_url_tree()` function as `index_site()`
- Add keyword argument `num_to_index` to `index_site()` function to allow crawler to stop indexing once it has found a predefined number of pages.

## 0.1.2a:

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

