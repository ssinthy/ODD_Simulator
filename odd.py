from enum import Enum
from operating_conditions import init_opcond_from_json

class Taxonomy:
    SPEED = "SPEED"
    EMERGENCY_VEHICLE = "EMERGENCY_VEHICLE"
    DISTANCE = "DISTANCE"
    EGO_VEHICLE = "EGO_VEHICLE"
    RELATIVE_POSITION = "RELATIVE_POSITION"

class OperationalDesignDomain:
    def __init__(self, odd_json=None):
        if odd_json is not None:
            self._in_opconditions = [init_opcond_from_json(json_incond) for json_incond in odd_json["conditions"]]
            return
        self._in_opconditions = []
    
    def add_in_operating_condition(self, opcond):
        self._in_opconditions.append(opcond)
    
    def check_within_odd(self, data):
        for incond in self._in_opconditions:
            if not incond.satisfy(data):
                return False
        return True
