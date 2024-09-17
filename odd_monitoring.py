import carla
import time
import requests
import math

from operating_conditions import OpCondImply, OpCondRange, OpCondSet, OpCondAnd, OpCondOr
from odd import OperationalDesignDomain, Taxonomy

INFINITY = 1000000000
odd = OperationalDesignDomain()

 # Fetch all ODDs from database and make odd objects
    # EMV on motoway must maintain a safe distance of 50m
odd.add_in_operating_condition(OpCondOr(opconds=[OpCondImply(opcond_if=OpCondAnd(
                                                            opconds=[
                                                                OpCondSet(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.RELATIVE_POSITION], boundset=["subject_lane"]),
                                                                OpCondRange(taxonomies=[Taxonomy.EGO_VEHICLE, Taxonomy.SPEED], min=0.0, max=70.0),
                                                                OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.SPEED], min=1.0, max=INFINITY)
                                                            ]),
                                                        opcond_then=OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.DISTANCE], min=50, max=INFINITY)
                                                            ),
                                            OpCondImply(opcond_if=OpCondAnd(
                                                            opconds=[
                                                                OpCondSet(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.RELATIVE_POSITION], boundset=["opposite_lane"]),
                                                                OpCondRange(taxonomies=[Taxonomy.EGO_VEHICLE, Taxonomy.SPEED], min=0.0, max=70.0),
                                                                OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.SPEED], min=1.0, max=INFINITY)
                                                            ]),
                                                            opcond_then=OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.DISTANCE], min=5, max=INFINITY),
                                                            ),
                                            OpCondImply(opcond_if=OpCondAnd(
                                                            opconds=[
                                                                OpCondSet(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.RELATIVE_POSITION], boundset=["subject_lane"]),
                                                                OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.SPEED], min=0.0, max=0.0),
                                                                OpCondRange(taxonomies=[Taxonomy.EGO_VEHICLE, Taxonomy.SPEED], min=0.0, max=70.0)
                                                            ]),
                                                            opcond_then=OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.DISTANCE], min=10, max=INFINITY),
                                                            ),
                                            OpCondImply(opcond_if=OpCondAnd(
                                                            opconds=[
                                                                OpCondSet(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.RELATIVE_POSITION], boundset=["opposite_lane"]),
                                                                OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.SPEED], min=0.0, max=0.0),
                                                                OpCondRange(taxonomies=[Taxonomy.EGO_VEHICLE, Taxonomy.SPEED], min=0.0, max=70.0)
                                                            ]),
                                                            opcond_then=OpCondRange(taxonomies=[Taxonomy.EMERGENCY_VEHICLE, Taxonomy.DISTANCE], min=3, max=INFINITY),
                                                            )
                                            ]))


def calculate_distance(ego_vehicle_location, emv_vehicle_location):
    """Calculate the Euclidean distance between two locations."""
    dx = ego_vehicle_location.x - emv_vehicle_location.x
    dy = ego_vehicle_location.y - emv_vehicle_location.y
    dz = ego_vehicle_location.z - emv_vehicle_location.z
    return math.sqrt(dx**2 + dy**2 + dz**2)

def is_emv_in_same_directional_lane(waypoint1, waypoint2):
    """Check if two waypoints are in the same directional lane based on lane ID sign."""
    return ((waypoint1.lane_id < 0 and waypoint2.lane_id < 0) or
            (waypoint1.lane_id > 0 and waypoint2.lane_id > 0))

def get_speed(vehicle):
    velocity = vehicle.get_velocity()
    # Calculate the magnitude of the velocity vector (speed)
    speed = math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
    # convert speed from m/s to km/h
    return speed * 3.6
