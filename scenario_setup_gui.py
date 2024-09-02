import tkinter as tk
from tkinter import ttk

from setup_carla import *
# Initialize the main window
root = tk.Tk()
root.title("ScenarioInfoManager")
root.geometry("600x400")  # Set the window size

# Default values for each field
default_values = {
    "road_type": "Motorway",
    "ego_vehicle_position": "Traffic Lane",
    "emv_position": "Same Road",
    "emv_direction": "Approaches from Behind",
    "weather_condition": "Clear",
    "time_of_day": "Day time",
    "safety_distance": "0",
}

# Dictionary to store previous values of comboboxes and spinbox
scenario_info = default_values.copy()

# Define the options for each combobox
road_type_options = ["Motorway", "Expressway"]
ego_vehicle_position_options = ["Traffic Lane", "Approaching Intersection"]
emv_position_options = ["Same Road", "Parallel Road", "Opposite Road", "Cross Road"]
emv_direction_options = ["Approaches from Behind", "As Lead Vehicle", "Approaches from Right Lane", "Approaches from Left Lane", "Approaches on Opposite Lane", 
                         "Approaches Intersection"]
weather_options = ["Clear", "Cloudy", "Light Rain", "Moderate Rain", "Heavy Rain"]
time_of_day_options = ["Day time", "Night time"]

spectator_spawn_point = 176
ego_spawn_point = 21
emv_spawn_point = 176
    
def map_scenario_for_motorway(scenario_info):
    if scenario_info["ego_vehicle_position"] == "Traffic Lane":
        pass
    elif scenario_info["ego_vehicle_position"] == "Approaching Intersection":
        pass
    elif scenario_info["ego_vehicle_position"] == "Approaching T-Junction":
        pass
        

# Function to handle the Start Simulation button click
def start_simulation():
    
    connect_to_carla()
    
    spawn_ego_vehicle(ego_spawn_point)
    
    spawn_emergency_vehicle(emv_spawn_point)
    
    set_spectator(spectator_spawn_point)

# Function to handle the Set Up Scenario button click
def setup_scenario():
    print(scenario_info)
    # map_user_input_to_carla_map(scenario_info)
    change_ego_vehicle_spawn_point(200)
    change_emv_vehicle_spawn_point(22)
            
# Function to handle value changes in comboboxes
def on_combobox_change(event, combobox_name):
    current_value = event.widget.get()  # Get the current value of the combobox
    if current_value != scenario_info[combobox_name]:
        print(f"{combobox_name} changed to {current_value}")
        scenario_info[combobox_name] = current_value  # Update the stored value

# Define a larger font
large_font = ("Helvetica", 14)

# Create and place the widgets
ttk.Label(root, text="Road Type", font=large_font).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
road_type_cb = ttk.Combobox(root, values=road_type_options, state="readonly", font=large_font)
road_type_cb.set(default_values["road_type"])
road_type_cb.grid(row=0, column=1, padx=20, pady=10)
road_type_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_change(event, "road_type"))

ttk.Label(root, text="Ego Vehicle Position", font=large_font).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
ego_vehicle_position_cb = ttk.Combobox(root, values=ego_vehicle_position_options, state="readonly", font=large_font)
ego_vehicle_position_cb.set(default_values["ego_vehicle_position"])
ego_vehicle_position_cb.grid(row=1, column=1, padx=20, pady=10)
ego_vehicle_position_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_change(event, "ego_vehicle_position"))

ttk.Label(root, text="Emergency Vehicle Position", font=large_font).grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
emv_position_cb = ttk.Combobox(root, values=emv_position_options, state="readonly", font=large_font)
emv_position_cb.set(default_values["emv_position"])
emv_position_cb.grid(row=2, column=1, padx=20, pady=10)
emv_position_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_change(event, "emv_position"))

ttk.Label(root, text="EMV Travel Direction", font=large_font).grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
emv_direction_cb = ttk.Combobox(root, values=emv_direction_options, state="readonly", font=large_font)
emv_direction_cb.set(default_values["emv_direction"])
emv_direction_cb.grid(row=3, column=1, padx=20, pady=10)
emv_direction_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_change(event, "emv_direction"))

ttk.Label(root, text="Weather Condition", font=large_font).grid(row=4, column=0, padx=20, pady=10, sticky=tk.W)
weather_cb = ttk.Combobox(root, values=weather_options, state="readonly", font=large_font)
weather_cb.set(default_values["weather_condition"])
weather_cb.grid(row=4, column=1, padx=20, pady=10)
weather_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_change(event, "weather_condition"))

ttk.Label(root, text="Time of Day", font=large_font).grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)
time_of_day_cb = ttk.Combobox(root, values=time_of_day_options, state="readonly", font=large_font)
time_of_day_cb.set(default_values["time_of_day"])
time_of_day_cb.grid(row=5, column=1, padx=20, pady=10)
time_of_day_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_change(event, "time_of_day"))

ttk.Label(root, text="Safety Distance (m)", font=large_font).grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)
safety_distance_sb = tk.Spinbox(root, from_=0, to=100, increment=1, font=large_font)
safety_distance_sb.grid(row=6, column=1, padx=20, pady=10)

start_button = ttk.Button(root, text="Start Simulation", command=start_simulation, style='TButton')
start_button.grid(row=7, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

'''
setup_button = ttk.Button(root, text="Set Up Scenario", command=setup_scenario, style='TButton')
setup_button.grid(row=8, column=0, columnspan=2, pady=10, ipadx=10, ipady=5)
'''
# Start the main event loop
root.mainloop()
