class ParsedXml:
    def __init__(self, id_, level, objects_names):
        self.id_ = id_
        self.level = level
        self.objects_names = objects_names

    def __eq__(self, other):
        return self.id_ == other.id_ and self.level == other.level and self.objects_names == other.objects_names

    def __repr__(self):
        return f'ParsedXml(id_={self.id_}, level={self.level}, len(objects_names)={len(self.objects_names)})'
