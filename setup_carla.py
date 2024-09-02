import carla

global_ego_vehicle = None
global_emv_vehicle = None
world = None
client = None

def connect_to_carla():
    global world, client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world("Town05")

# TODO Separate ego vehicle and emv spawning
def spawn_ego_vehicle(ego_spawn_point):
    global global_ego_vehicle, world
    # Spawn an emergency vehicle town 5 spawn point 108 / HH map 154
    spawn_points = world.get_map().get_spawn_points()
    vehicle_bp = world.get_blueprint_library().find('vehicle.audi.etron')
    global_ego_vehicle = world.try_spawn_actor(vehicle_bp, spawn_points[ego_spawn_point])
    global_ego_vehicle.set_autopilot(True)
    
def spawn_emergency_vehicle(emv_spawn_point):
    global global_emv_vehicle, world, client
    spawn_points = world.get_map().get_spawn_points()
    
    emergency_bp = world.get_blueprint_library().find('vehicle.carlamotors.firetruck')
    global_emv_vehicle = world.spawn_actor(emergency_bp, spawn_points[emv_spawn_point])
    traffic_manager = client.get_trafficmanager()
    traffic_manager_port = traffic_manager.get_port()

    # Set the vehicle to drive 30% faster than the current speed limit
    traffic_manager.vehicle_percentage_speed_difference(global_emv_vehicle, -30)  # No speed variation
    
    # Make the vehicle ignore traffic lights
    traffic_manager.ignore_lights_percentage(global_emv_vehicle, 100)
    
    # Turn on the vehicle's (emergency lights)
    from carla import VehicleLightState as vls
    global_emv_vehicle.set_light_state(carla.VehicleLightState(vls.Special1))
        
    global_emv_vehicle.set_autopilot(True, traffic_manager_port)
    
def change_ego_vehicle_spawn_point(ego_spawn_point):
    global global_ego_vehicle
    
    global_ego_vehicle.destroy()
    
    spawn_ego_vehicle(ego_spawn_point)
    
def change_emv_vehicle_spawn_point(emv_spawn_point):
    global global_emv_vehicle

    global_emv_vehicle.destroy()
    
    spawn_emergency_vehicle(emv_spawn_point)
    
def set_spectator(spectator_spawn_point):
    spawn_points = world.get_map().get_spawn_points()
    spectator = world.get_spectator()
    spawn_point_motor_way = spawn_points[spectator_spawn_point]
    
    spectator_pos_motorway = carla.Transform(spawn_point_motor_way.location + carla.Location(x=20,z=8),
                        carla.Rotation(yaw = spawn_point_motor_way.rotation.yaw))
    spectator.set_transform(spectator_pos_motorway)       
