def score_group(pred1, pred2):
    """
    pred1, pred2: tuples like ('NZ', 'SA')
    returns score in {0, 1, 2, 4}
    """
    if pred1 == pred2:
        return 4

    set1, set2 = set(pred1), set(pred2)

    if set1 == set2:
        return 2

    if len(set1 & set2) == 1:
        return 1

    return 0

def model_similarity(model_a, model_b):
    """
    model_a, model_b: dicts {group: (first, second)}
    returns normalized similarity in [0, 1]
    """
    total_score = 0
    max_score = 4 * len(model_a)

    for group in model_a:
        total_score += score_group(model_a[group], model_b[group])

    return total_score / max_score

model_1 = {
    'A': ('IND', 'PAK'),
    'B': ('AUS', 'SL'),
    'C': ('ENG', 'WI'),
    'D': ('SA', 'NZ')
}

model_2 = {
    'A': ('PAK', 'IND'),   # swapped
    'B': ('AUS', 'SL'),    # exact
    'C': ('ENG', 'BAN'),   # one overlap
    'D': ('NZ', 'SA')      # swapped
}

sim = model_similarity(model_1, model_2)
print(sim) 
