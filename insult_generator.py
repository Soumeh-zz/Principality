from random import choicedef generate_insult(safe=False):
    main = ['well played (noun)', 'you are (adjct) (noun)', 'you are (adjct) (noun)', 'eat a (noun) (noun)',    'eat a (noun)', '(verb)', 'i will (verb) you', 'who is this (adjct) (noun)']
    insults = {
    "noun": ['nerd', 'weakling', 'dork', 'donkey', 'maggot', 'cretin', 'jerk', 'idiot', 'fool', 'butt', 'nerd', 'freak', 'buffoon', 'tool',    'dunce', 'blockhead', 'pinhead', 'chump', 'donkey', 'muppet'],    "verb": ['kiss', 'kick', 'punch'],
    "adjct": ['french', 'stupid', 'weak', 'dumb', 'fat', 'ugly', 'thick', 'daft', 'long', 'tiny', 'bumbling', 'absolute']
    }
    if not safe:
        main += ['i will (verb) your mother', '(verb) yourself', '(verb) you', 'i (verb) in your room', 'choke on a (noun) and (verb)']        newInsults = {        "noun": ['retard', 'fuck', 'shit', 'ass', 'imbecile', 'ass', 'asshole', 'turd', 'sucker', 'piss', 'bitch', 'tard', 'fuckhead'],        "verb": ['fuck', 'shit', 'kill', 'shit', 'hang', 'pass'],        "adjct": ['retarded', 'motherfucking']        }        for key, values in newInsults.items():            for value in values:                insults[key].append(value)    insult = choice(main)
    for key, key_insults in insults.items():
        key = '(' + key + ')'
        while key in insult:            print(key_insults)
            insult = insult.replace(key, choice(key_insults), 1)
    remove_characters = choice(range(-2, 3))
    while remove_characters > 0:
        insult = insult.replace(insult[choice(range(len(insult)))], '', 1)
        remove_characters -= 1
    return insult