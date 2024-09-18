import carla
import time
import math
import threading

INFINITY = 1000000
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

# Function to calculate rotated points
def rotate_point(x, y, theta):
    x_rot = x * math.cos(theta) - y * math.sin(theta)
    y_rot = x * math.sin(theta) + y * math.cos(theta)
    return x_rot, y_rot

# Function to draw the safety boundary
def draw_safety_boundary(ego_location, ego_rotation, status, d_front, d_rear, d_left, d_right):
    color = carla.Color(0, 255, 0) if status == "in" else carla.Color(255, 0, 0)
    # Ego vehicle heading (in radians)
    yaw = math.radians(ego_rotation.yaw)

    # Define the corners of the safety boundary
    corners = [
        # Front-left corner
        (ego_location.x + d_front, ego_location.y + d_left),
        # Front-right corner
        (ego_location.x + d_front, ego_location.y - d_right),
        # Rear-left corner
        (ego_location.x - d_rear, ego_location.y + d_left),
        # Rear-right corner
        (ego_location.x - d_rear, ego_location.y - d_right)
    ]

    # Rotate the points based on the vehicle's yaw (heading)
    rotated_corners = []
    for corner in corners:
        x_rot, y_rot = rotate_point(corner[0] - ego_location.x, corner[1] - ego_location.y, yaw)
        rotated_corners.append(carla.Location(x=ego_location.x + x_rot, y=ego_location.y + y_rot, z=ego_location.z))

    # Draw lines between the rotated corners to form the boundary box
    world.debug.draw_line(rotated_corners[0], rotated_corners[1], thickness=0.3, color=color, life_time=0.01)  # Front line
    world.debug.draw_line(rotated_corners[1], rotated_corners[3], thickness=0.3, color=color, life_time=0.01)  # Right line
    world.debug.draw_line(rotated_corners[3], rotated_corners[2], thickness=0.3, color=color, life_time=0.01)  # Rear line
    world.debug.draw_line(rotated_corners[2], rotated_corners[0], thickness=0.3, color=color, life_time=0.01)  # Left line

# ODD Monitoring   
def check_safety_boundary(d_front, d_rear, d_left, d_right):
    global global_emv_vehicle, world, global_ego_vehicle

    # Reset the event
    stop_event_odd_monitoring.clear()
    height = 2.0  

    while True:
        time.sleep(0.01)
        if global_ego_vehicle is None or global_emv_vehicle is None:
            break   
        if stop_event_odd_monitoring.is_set() or stop_event_simulation.is_set():
            break

         # Get the current location of the vehicle
        ego_vehicle_transform = global_ego_vehicle.get_transform()
        ego_location = ego_vehicle_transform.location
        emergency_vehicle_transform = global_emv_vehicle.get_transform()
        emv_location = emergency_vehicle_transform.location
        ego_rotation = ego_vehicle_transform.rotation
        yaw_ego = math.radians(ego_vehicle_transform.rotation.yaw)

        dx = emv_location.x - ego_location.x
        dy = emv_location.y - ego_location.y
        
        # Rotate the relative position to align with the ego vehicle's orientation (local coordinates)
        dx_local, dy_local = rotate_point(dx, dy, -yaw_ego)

        # Check if the emergency vehicle is within the longitudinal and lateral safety boundaries
        within_longitudinal_bounds = (-d_rear <= dx_local <= d_front)  # Check front and rear
        within_lateral_bounds = (-d_right <= dy_local <= d_left)
        
        if within_longitudinal_bounds and within_lateral_bounds:
            # Draw the bounding box in the world for visualization (duration = 0.1 seconds, color = green) out of ODD
            # world.debug.draw_box(bounding_box, ego_rotation, thickness=0.2, color=carla.Color(255, 0, 0, 0), life_time=0.1)
            world.debug.draw_string(ego_location, "Out of ODD", draw_shadow=False, color=carla.Color(255,0,0), life_time=0.01)
            draw_safety_boundary(ego_location, ego_rotation, "out", d_front, d_rear, d_left, d_right)
        else:
            # Draw the bounding box in the world for visualization (duration = 0.1 seconds, color = green)
            draw_safety_boundary(ego_location, ego_rotation, "in", d_front, d_rear, d_left, d_right)
