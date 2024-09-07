import carla
import random
import time
import math

def main():
    # Connect to the Carla server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    spectator = world.get_spectator()
    
    # Get a blueprint library and choose a vehicle blueprint
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter('vehicle.*')[0]  # Use the first vehicle blueprint

    # Get a random spawn point
    spawn_points = world.get_map().get_spawn_points()
    spawn_point = spawn_points[1]

    # Spawn the vehicle
    # vehicle = world.spawn_actor(vehicle_bp, spawn_point)
    
    transform = carla.Transform(spawn_point.location + carla.Location(x=20, y=10, z=4),
                                carla.Rotation(yaw = spawn_point.rotation.yaw - 155))
    spectator.set_transform(transform)
    
if __name__ == '__main__':
    main()
