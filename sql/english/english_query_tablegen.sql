ALTER TABLE pg_translation_en
    ADD news_source varchar(64);
	
UPDATE pg_translation_en
    SET news_source = b.news_source 
        FROM pg_page b
            WHERE pg_translation_en.uid = b.uid;

ALTER TABLE pg_translation_en
    ADD search_tsvectors_en tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', pg_translation_en.translation_text), 'A') || ' ' ||
            setweight(to_tsvector('english', pg_translation_en.news_source), 'D')) STORED;
