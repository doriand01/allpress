import logging

logging.basicConfig(format='[%(levelname)s];%(asctime)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO,
                    filename='app.log',
                    filemode='a',
    )

POSTGRESQL_SERVER_HOST     = '127.0.0.1'
POSTGRESQL_DATABASE_NAME   = 'postgres'
POSTGRESQL_USERNAME        = 'postgres'
POSTGRESQL_PASSWORD        = 'test0000'

URL_REGEX = '((http|https):\/\/)?(((www|ww\d|www\d)\.)?(?=.{5,255})([\w-]{2,63}\.)+\w{2,63})(\/[\w\-._~:?#@!$&\'\(\)*+,;%=]+)*\/?'
HREF_PARSE_REGEX = '(?<=<a\shref=([\'"]))([\w\-._~:?#@!$&/\'\(\)*+,;%=]+)\1'

CONTINENTS = [
    'Africa',
    'Asia',
    'Europe',
    'North America',
    'South America',
    'Oceania'
]

NEWS_SOURCE_CATALOG_FILE = 'C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\allpress\\sources.csv'
WEB_CRAWLER_OUTPUT_FOLDER = 'C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\allpress\\crawler_index'

EQUATORIAL_CIRCUMFERENCE = 24901.0
MERIDIONAL_CIRCUMFERENCE = 24860.0


VALID_UNITS = ['degrees', 'deg', 'miles', 'mi', 'kilometers', 'kilometres', 'km']

LINGUA_SUPPORTED_LANGUAGES = [
    'AFRIKAANS', 'ALBANIAN', 'ARABIC', 'ARMENIAN', 'AZERBAIJANI', 
    'BASQUE', 'BELARUSIAN', 'BENGALI', 'BOKMAL', 'BOSNIAN', 
    'BULGARIAN', 'CATALAN', 'CHINESE', 'CROATIAN', 'CZECH', 
    'DANISH', 'DUTCH', 'ENGLISH', 'ESPERANTO', 'ESTONIAN', 
    'FINNISH', 'FRENCH', 'GANDA', 'GEORGIAN', 'GERMAN', 'GREEK',
    'GUJARATI', 'HEBREW', 'HINDI', 'HUNGARIAN', 'ICELANDIC', 
    'INDONESIAN', 'IRISH', 'ITALIAN', 'JAPANESE', 'KAZAKH', 
    'KOREAN', 'LATIN', 'LATVIAN', 'LITHUANIAN', 'MACEDONIAN', 
    'MALAY', 'MAORI', 'MARATHI', 'MONGOLIAN', 'NYNORSK', 
    'PERSIAN', 'POLISH', 'PORTUGUESE', 'PUNJABI', 'ROMANIAN', 
    'RUSSIAN', 'SERBIAN', 'SHONA', 'SLOVAK', 'SLOVENE', 
    'SOMALI', 'SOTHO', 'SPANISH', 'SWAHILI', 'SWEDISH', 
    'TAGALOG', 'TAMIL', 'TELUGU', 'THAI', 'TSONGA', 'TSWANA', 
    'TURKISH', 'UKRAINIAN', 'URDU', 'VIETNAMESE', 'WELSH', 
    'XHOSA', 'YORUBA', 'ZULU'
]