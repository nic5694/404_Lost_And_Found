import datetime

class LostItem():
    def __init__(self, id, image_url, description, location):
        self.id = id
        self.description = description
        self.image_url = image_url
        self.location = location
        self.time_found = datetime.datetime.now()
        self.is_claimed = False