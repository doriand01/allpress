ALTER TABLE pg_translation_en
    ADD search_tsvectors tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('spanish', pg_translation_en.news_source), 'A')
) STORED;