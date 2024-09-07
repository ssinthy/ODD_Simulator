import carla
import time
import math
import random

global_ego_vehicle = None
global_emv_vehicle = None
world = None
client = None

# To import a basic agent
from agents.navigation.basic_agent import BasicAgent

# To import a behavior agent
from agents.navigation.behavior_agent import BehaviorAgent

def connect_to_carla():
    global world, client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world("Town03")

# TODO Separate ego vehicle and emv spawning
def spawn_ego_vehicle(ego_spawn_point = 41):
    global global_ego_vehicle, world
    # Spawn an emergency vehicle town 5 spawn point 108 / HH map 154
    spawn_points = world.get_map().get_spawn_points()
    vehicle_bp = world.get_blueprint_library().find('vehicle.audi.etron')
    global_ego_vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[ego_spawn_point])
    
def spawn_emergency_vehicle(emv_spawn_point = 231):
    global global_emv_vehicle, world, client
    spawn_points = world.get_map().get_spawn_points()
    
    emergency_bp = world.get_blueprint_library().find('vehicle.dodge.charger_police')
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

def activate_autopilot(emv_position):
    global global_ego_vehicle, global_emv_vehicle
    spawn_points = world.get_map().get_spawn_points()
    
    ego_agent = BasicAgent(global_ego_vehicle)
    emv_agent = BasicAgent(global_emv_vehicle)

    destination = spawn_points[180].location
    destination_ego = spawn_points[171].location
    
    ego_agent.set_destination(destination_ego)
    ego_agent.follow_speed_limits(value=False)
    ego_agent.set_target_speed(100)
    ego_agent.ignore_traffic_lights(active=True)
    
    emv_agent.set_destination(destination)
    emv_agent.follow_speed_limits(value=False)
    emv_agent.set_target_speed(100) # km/h
    emv_agent.ignore_traffic_lights(active=True)
    
    while True:
        if ego_agent.done():
            print("The target has been reached, stopping the simulation")
            break
        global_ego_vehicle.apply_control(ego_agent.run_step())
        global_emv_vehicle.apply_control(emv_agent.run_step())
        
        velocity_vector = global_emv_vehicle.get_velocity()
        speed_mps = math.sqrt(velocity_vector.x**2 + velocity_vector.y**2 + velocity_vector.z**2)
        speed_kmh = speed_mps * 3.6
        print(f"Current speed: {speed_kmh:.2f} km/h")
        
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

    # Pause to observe the movement
    time.sleep(2)

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