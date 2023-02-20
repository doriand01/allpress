SELECT translation_text, uid, title
    ts_rank(search_tsvectors_en, websearch_to_tsquery($$english$$, QUERYVAL)) +
    ts_rank(search_tsvectors_en, websearch_to_tsquery($$simple$$, QUERYVAL))
as rank
    FROM pg_translation_en
    WHERE search_tsvectors_en @@ websearch_to_tsquery($$english$$, QUERYVAL)
        OR search_tsvectors_en @@ websearch_to_tsquery($$simple$$, QUERYVAL)
    ORDER BY rank desc;