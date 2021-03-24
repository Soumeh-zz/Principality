from os import listdir
from hashlib import sha256

old_hashes = {}

def check_changes(location=None):
    global old_hashes
    hashes = {}
    changes_list = []
    files = [f for f in listdir(location) if f.endswith('.py')][:100]
    changed = []
    for file in files:
        h = sha256()
        mv = memoryview(bytearray(131072))
        path = ''
        if location:
            path += location + '/'
        with open(path + file, 'rb', buffering=0) as f:
            for n in iter(lambda : f.readinto(mv), 0):
                h.update(mv[:n])
        hashes[file] = h.hexdigest()[:10]
        try:
            if old_hashes[file] != hashes[file]:
                changed.append(file)
        except KeyError:
            pass
    if not old_hashes:
        old_hashes = hashes
        return {}
    changes_list.append(changed)
    added = list(set(hashes.keys()) - set(old_hashes.keys()))
    changes_list.append(added)
    removed = list(set(old_hashes.keys()) - set(hashes.keys()))
    changes_list.append(removed)
    old_hashes = hashes
   #return [ [changed], [added], [removed] ]
    return changes_list