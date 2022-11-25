import allpress
import csv

crawl1 = allpress.web.Crawler('https://tesfanews.net', 'Tesfa News')
crawl2 = allpress.web.Crawler('https://www.clarin.com/', 'Clarin Digital')
crawl2.index_site()
crawl1.index_site()
models1 = allpress.models.create_page_models(list(crawl1.total_parsed), 'Tesfa News')
models2 = allpress.models.create_page_models(list(crawl2.total_parsed), 'Clarin Digital')
transmods1 = []
transmods2 = []
for mods1 in models1:
    transmods1.append(allpress.models.create_translation_model(mods1))
    
for mods2 in models2:
    transmods2.append(allpress.models.create_translation_model(mods2))
allpress.cursor.migrate_pages_to_db(models2)
allpress.cursor.migrate_pages_to_db(models1)
allpress.cursor.migrate_translations_to_db(transmods1)
allpress.cursor.migrate_translations_to_db(transmods2)