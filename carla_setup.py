import carla
import time
import math

global_ego_vehicle = None
global_emv_vehicle = None
world = None
client = None

# To import a basic agent
from agents.navigation.basic_agent import BasicAgent

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
        
def change_vehicle_position(distance, vehicle_type):
    global global_ego_vehicle, global_emv_vehicle
    
    current_vehicle = global_emv_vehicle if vehicle_type != "ego" else global_ego_vehicle
    
    transform = current_vehicle.get_transform()
    location = transform.location
    rotation = transform.rotation

    # Calculate the forward offset based on the vehicle's rotation
    forward_distance = distance  # Distance to move forward (1 meter)
    rad_yaw = math.radians(rotation.yaw)  # Convert yaw to radians

    # Update location to move 1 meter forward
    new_x = location.x + forward_distance * math.cos(rad_yaw)
    new_y = location.y + forward_distance * math.sin(rad_yaw)
    new_location = carla.Location(new_x, new_y, location.z)

    # Set the new transform with the updated location
    new_transform = carla.Transform(new_location, rotation)
    current_vehicle.set_transform(new_transform)

def map_destination(scenario_info):
    spawn_points = world.get_map().get_spawn_points()

    if scenario_info["ev_action"] == "Go Straight":
        destination_ego = spawn_points[180].location
    elif scenario_info["ev_action"] == "Go Straight and Turn Left" or scenario_info["ev_action"] == "Turn Left":
        destination_ego = spawn_points[87].location
    elif scenario_info["ev_action"] == "Go Straight and Turn Right" or scenario_info["ev_action"] == "Turn Right":
        destination_ego = spawn_points[35].location

    if  scenario_info["emv_position"] == "Ego Lane" or scenario_info["emv_position"] == "Parallel Lane":
        if scenario_info["emv_action"] == "Go Straight":
            destination_emv = spawn_points[179].location
        elif scenario_info["emv_action"] == "Go Straight and Turn Left":
            destination_emv = spawn_points[88].location
        elif scenario_info["emv_action"] == "Go Straight and Turn Right":
            destination_emv = spawn_points[36].location
    elif  scenario_info["emv_position"] == "Approaches Intersection" or scenario_info["emv_position"] == "Cross Road":
        if scenario_info["emv_action"] == "Go Straight":
            destination_emv = spawn_points[88].location
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


def activate_autopilot(ego_velocity, emv_velocity, scenario_info):
    global global_ego_vehicle, global_emv_vehicle
    
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
    # emv_agent.ignore_vehicles(active=True)
    
    
    while True:
        if ego_agent.done() and emv_agent.done():
            print("The target has been reached, stopping the simulation")
            break
        global_ego_vehicle.apply_control(ego_agent.run_step())
        global_emv_vehicle.apply_control(emv_agent.run_step())
        