import allpress
import csv

csvfile = "C:\\Users\\preit\\OneDrive\\Desktop\\coding projects\\allpress\\sources.csv"
file = open(csvfile, 'r')
reader = csv.reader(file, delimiter=',')
sources = [line for line in reader]
sources = sources[1:]
for source in sources:
    crawler = allpress.web.Crawler(source[4], source[2])
    crawler.index_site()
    models = allpress.models.create_page_models(list(crawler.total_parsed), crawler.source_name)
    transmods = []
    for model in models:
        transmods.append(allpress.models.create_translation_model(model))
    allpress.cursor.migrate_pages_to_db(models)
    allpress.cursor.migrate_translations_to_db(transmods)

results = allpress.graphic_search_by_text('Climate change', language='EN')
print(results)