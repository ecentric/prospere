from prospere.contrib.cabinet.models import StorageBans

def add_ban(storage):
    StorageBans.object.create(storage = storage)
