from concurrent.futures import process
import spacy


processor = spacy.load("en_core_web_sm")


def Sort_Tuple(tup):
     
    # getting length of list of tuples
    lst = len(tup)
    for i in range(0, lst):
         
        for j in range(0, lst-i-1):
            if (tup[j][1] > tup[j + 1][1]):
                temp = tup[j]
                tup[j]= tup[j + 1]
                tup[j + 1]= temp
    return tup


def calculate_named_entity_instance(text: str) -> list:
    processed = processor(text)
    text_list = text.lower()
    named_entities = [entity.text.lower() for entity in processed.ents]
    named_entity_instances = []
    for entity in named_entities:
        entity_count = text_list.count(entity)
        named_entity_instances.append((entity, entity_count))
    named_entity_instances_sorted = Sort_Tuple(named_entity_instances)
    return reversed(named_entity_instances_sorted)


def calculate_verb_instance(text: str):
    processed = processor(text)
    tokens = [token for token in processed]
    text_list = text.lower()
    verbs = [verb for verb in tokens if verb.pos_ == 'VERB']
    verb_instances = []
    for verb in verbs:
        entity_count = text_list.count(verb.text)
        verb_instances.append((verb.text.lower(),  entity_count))
    verb_instances_sorted = Sort_Tuple(verb_instances)
    return reversed(verb_instances_sorted)
