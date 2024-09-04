import carla
import time

global_ego_vehicle = None
global_emv_vehicle = None
world = None
client = None

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
    
    emergency_bp = world.get_blueprint_library().find('vehicle.carlamotors.firetruck')
    global_emv_vehicle = world.spawn_actor(emergency_bp, spawn_points[emv_spawn_point])
    
    # Turn on the vehicle's (emergency lights)
    from carla import VehicleLightState as vls
    global_emv_vehicle.set_light_state(carla.VehicleLightState(vls.Special1))   
    
def set_spectator(desired_location = carla.Location(x=24.953684, y=201.391769, z=118.926270), desired_rotation = carla.Rotation(pitch=-64.051315, yaw=-90.070381, roll=0)):
    spectator = world.get_spectator()
    desired_transform = carla.Transform(desired_location, desired_rotation)
    spectator.set_transform(desired_transform)

def activate_autopilot():
    global global_ego_vehicle, global_emv_vehicle
    
    global_ego_vehicle.set_autopilot(True)

    traffic_manager = client.get_trafficmanager()
    traffic_manager_port = traffic_manager.get_port()

    # Set the vehicle to drive 30% faster than the current speed limit
    traffic_manager.vehicle_percentage_speed_difference(global_emv_vehicle, -30)  # No speed variation
    
    # Make the vehicle ignore traffic lights
    traffic_manager.ignore_lights_percentage(global_emv_vehicle, 100)

    global_emv_vehicle.set_autopilot(True, traffic_manager_port)

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