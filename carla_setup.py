import carla
import time
import math
import threading

from odd_monitoring import *

global_ego_vehicle = None
global_emv_vehicle = None
world = None
client = None

# To import a basic agent
from agents.navigation.basic_agent import BasicAgent

stop_event_odd_monitoring = threading.Event()
stop_event_simulation = threading.Event()

def connect_to_carla():
    global world, client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world("Town03")

def spawn_ego_vehicle(ego_spawn_point = 41):
    global global_ego_vehicle, world
    spawn_points = world.get_map().get_spawn_points()
    vehicle_bp = world.get_blueprint_library().find('vehicle.audi.etron')
    global_ego_vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[ego_spawn_point])
    
def spawn_emergency_vehicle(emv_spawn_point = 231):
    global global_emv_vehicle, world, client
    spawn_points = world.get_map().get_spawn_points()
    
    emergency_bp = world.get_blueprint_library().find('vehicle.dodge.charger_police_2020')
    global_emv_vehicle = world.spawn_actor(emergency_bp, spawn_points[emv_spawn_point])
    
    # Turn on the vehicle's (emergency lights)
    from carla import VehicleLightState as vls
    global_emv_vehicle.set_light_state(carla.VehicleLightState(vls.Special1))  
    
def set_spectator():
    desired_location = carla.Location(x=10.029333, y=197.808701, z=102.078331)
    desired_rotation = carla.Rotation(pitch=-55.972248, yaw=-88.135925, roll=0)
    spectator = world.get_spectator()
    desired_transform = carla.Transform(desired_location, desired_rotation)
    spectator.set_transform(desired_transform)

def map_scenario_for_motorway_same_lane_and_parallel_lane(scenario_info):
    if  scenario_info["emv_position"] == "Ego Lane":
        if  scenario_info["emv_direction"] == "Approaches from Behind":
            change_emv_vehicle_spawn_point(231)
        elif  scenario_info["emv_direction"] == "As Lead Vehicle":
            change_emv_vehicle_spawn_point(37)
    elif scenario_info["emv_position"] == "Parallel Lane":
        if  scenario_info["emv_direction"] == "Approaches from Behind":
            change_emv_vehicle_spawn_point(230)
        elif  scenario_info["emv_direction"] == "As Lead Vehicle":
            change_emv_vehicle_spawn_point(38)
    elif scenario_info["emv_position"] == "Opposite Lane":
        change_emv_vehicle_spawn_point(118)
    elif scenario_info["emv_position"] == "Cross Road":
        change_emv_vehicle_spawn_point(157)
    elif scenario_info["emv_position"] == "Parked":
        change_emv_vehicle_spawn_point(207)
    elif scenario_info["emv_position"] == "Approaches Intersection":
        change_emv_vehicle_spawn_point(69)
        
def change_vehicle_position(distance, vehicle_type, action):
    global global_ego_vehicle, global_emv_vehicle
    
    current_vehicle = global_emv_vehicle if vehicle_type != "ego" else global_ego_vehicle
    
    transform = current_vehicle.get_transform()
    location = transform.location
    rotation = transform.rotation

    # Calculate the forward offset based on the vehicle's rotation
    rad_yaw = math.radians(rotation.yaw)  # Convert yaw to radians

    if action == "forward":
        new_x = location.x + distance * math.cos(rad_yaw)
        new_y = location.y + distance * math.sin(rad_yaw)
        new_location = carla.Location(new_x, new_y, location.z)
    elif action == "backward":
        new_x = location.x - distance * math.cos(rad_yaw)
        new_y = location.y - distance * math.sin(rad_yaw)
        new_location = carla.Location(new_x, new_y, location.z)

    # Set the new transform with the updated location
    new_transform = carla.Transform(new_location, rotation)
    current_vehicle.set_transform(new_transform)

def map_destination(scenario_info):
    spawn_points = world.get_map().get_spawn_points()

    if scenario_info["ev_action"] == "Go Straight":
        destination_ego = spawn_points[180].location
    elif scenario_info["ev_action"] == "Go Straight and Turn Left" or scenario_info["ev_action"] == "Turn Left":
        destination_ego = carla.Location(x=86.572197, y=133.357605, z=0.078843)
    elif scenario_info["ev_action"] == "Go Straight and Turn Right" or scenario_info["ev_action"] == "Turn Right":
        destination_ego = spawn_points[35].location

    if  scenario_info["emv_position"] == "Ego Lane" or scenario_info["emv_position"] == "Parallel Lane":
        if scenario_info["emv_action"] == "Go Straight":
            destination_emv = spawn_points[179].location
        elif scenario_info["emv_action"] == "Go Straight and Turn Left":
            destination_emv = carla.Location(x=100, y=133.357605, z=0.078843)
        elif scenario_info["emv_action"] == "Go Straight and Turn Right":
            destination_emv = spawn_points[36].location
    elif  scenario_info["emv_position"] == "Approaches Intersection" or scenario_info["emv_position"] == "Cross Road":
        if scenario_info["emv_action"] == "Go Straight":
            destination_emv = carla.Location(x=100, y=133.357605, z=0.078843)
        elif scenario_info["emv_action"] == "Turn Left":
            destination_emv = spawn_points[68].location
        elif scenario_info["emv_action"] == "Turn Right":
            destination_emv = spawn_points[179].location
    elif scenario_info["emv_position"] == "Parked":
        destination_emv = spawn_points[207].location

    return destination_ego, destination_emv

def destroy_ego_vehicle():
    global global_ego_vehicle

    if global_ego_vehicle != None:
        global_ego_vehicle.destroy()

def destroy_emv_vehicle():
    global global_emv_vehicle

    if global_emv_vehicle != None:
        global_emv_vehicle.destroy()
    
def change_ego_vehicle_spawn_point(ego_spawn_point):
    destroy_ego_vehicle()
    spawn_ego_vehicle(ego_spawn_point)
    
def change_emv_vehicle_spawn_point(emv_spawn_point):
    destroy_emv_vehicle()
    spawn_emergency_vehicle(emv_spawn_point)

def stop_simulation():
    stop_event_simulation.set()
    stop_event_odd_monitoring.set()
    destroy_ego_vehicle()
    destroy_emv_vehicle()


def activate_autopilot(ego_velocity, emv_velocity, scenario_info):
    global global_ego_vehicle, global_emv_vehicle

    # Reset the event
    stop_event_simulation.clear()
    
    ego_agent = BasicAgent(global_ego_vehicle)
    emv_agent = BasicAgent(global_emv_vehicle)
    ego_agent.ignore_traffic_lights(active=True)
    emv_agent.ignore_traffic_lights(active=True)

    ego_agent.follow_speed_limits(value=False)
    emv_agent.follow_speed_limits(value=False)

    destination_ego, destination_emv = map_destination(scenario_info)
    
    ego_agent.set_destination(destination_ego)
    ego_agent.set_target_speed(ego_velocity)
    
    emv_agent.set_destination(destination_emv)
    emv_agent.set_target_speed(emv_velocity)
    emv_agent.ignore_stop_signs(active=True)
    
    
    while True:
        if global_ego_vehicle is None or global_emv_vehicle is None:
            break
        if stop_event_odd_monitoring.is_set() or stop_event_simulation.is_set():
            break
        if ego_velocity == 0 and emv_velocity == 0:
            break
        if ego_agent.done():
            print("The target has been reached, stopping the simulation")
            # Signal the worker thread to stop
            stop_event_odd_monitoring.set()
            break
        global_ego_vehicle.apply_control(ego_agent.run_step())
        global_emv_vehicle.apply_control(emv_agent.run_step())
        
def monitor_odd():
    global global_emv_vehicle, world, global_ego_vehicle

    # Reset the event
    stop_event_odd_monitoring.clear()

    map = world.get_map()

    while True:
        time.sleep(0.1)
        if global_ego_vehicle is None or global_emv_vehicle is None:
            break   
        if stop_event_odd_monitoring.is_set() or stop_event_simulation.is_set():
            break

         # Get the current location of the vehicle
        ego_vehicle_location = global_ego_vehicle.get_location()
        emergency_vehicle_location = global_emv_vehicle.get_location()
       
        # Get the road ID and check if it's a junction for ego vehicle
        waypoint_ego = map.get_waypoint(ego_vehicle_location)

        # Get the road ID and check if it's a junction for emv vehicle
        waypoint_emv = map.get_waypoint(emergency_vehicle_location)

        # Get ego vehicle velocity
        ego_vehicle_velocity = get_speed(global_ego_vehicle)

        # Get emergency vehicle velocity
        emergency_vehicle_velocity = get_speed(global_emv_vehicle)

        emv_relative_pos = "on_other_road"

        if waypoint_emv.is_junction:
            emv_relative_pos = "on_junction"

        if waypoint_ego.road_id == waypoint_emv.road_id:
            # Check the condition and set lane_type if condition is true
            if is_emv_in_same_directional_lane(waypoint_ego, waypoint_emv):
                if is_emv_in_on_ego_lane(waypoint_ego, waypoint_emv):
                    emv_relative_pos = "subject_lane"
                else:
                    emv_relative_pos = "parallel lane"
            else:
                emv_relative_pos = "opposite_lane"

        distance_between_ego_and_emv = calculate_distance(ego_vehicle_location, emergency_vehicle_location)

        # Construct avdata from road info. Include all necessary information in avdata
        avdata = {
            Taxonomy.EGO_VEHICLE: {
                Taxonomy.SPEED: round(ego_vehicle_velocity, 2)
            },
            Taxonomy.EMERGENCY_VEHICLE: {
                Taxonomy.SPEED: round(emergency_vehicle_velocity, 2),
                Taxonomy.DISTANCE: round(distance_between_ego_and_emv, 2),
                Taxonomy.RELATIVE_POSITION: emv_relative_pos
            }
        }

        print(avdata)

        # Evaluate the avdata against ODD

        is_within_odd = odd.check_within_odd(avdata)

        if is_within_odd:
            print("Inside ODD")
        else:
            print("Outside ODD")
            world.debug.draw_string(ego_vehicle_location, "Out of ODD", draw_shadow=False, color=carla.Color(255,0,0), life_time=0.1)
            bbox = global_ego_vehicle.bounding_box
            bbox.location += global_ego_vehicle.get_transform().location

            # Draw the bounding box
            world.debug.draw_box(bbox, global_ego_vehicle.get_transform().rotation, thickness=0.1, color=carla.Color(255, 0, 0, 0), life_time=0.1)