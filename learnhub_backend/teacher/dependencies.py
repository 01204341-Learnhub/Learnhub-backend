from bson.objectid import ObjectId


class _Program:
    def __init__(self, program_id: str | ObjectId, _type: str):
        if type(program_id) == str:
            self.program_id: str = program_id
        else:
            self.program_id: str = str(program_id)
        self.type: str = _type
