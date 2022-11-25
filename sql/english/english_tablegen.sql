ALTER TABLE pg_translation_en
    ADD search_tsvectors tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', pg_translation_en.translation_text), 'A')
) STORED;