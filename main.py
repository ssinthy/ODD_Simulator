import tkinter as tk
from tkinter import ttk
import threading

from carla_setup import *

# Default values for each field
default_values = {
    "road_type": "Motorway",
    "ego_vehicle_position": "Traffic Lane",
    "emv_position": "Ego Lane",
    "emv_direction": "Approaches from Behind",
    "ev_action": "Go Straight",
    "emv_action": "Go Straight"
}

# Dictionary to store previous values of comboboxes and spinbox
scenario_info = default_values.copy()

# Define the options for each combobox
road_type_options = ["Motorway"]
ego_vehicle_position_options = ["Traffic Lane", "Approaching Intersection"]
emv_position_options = ["Ego Lane", "Parallel Lane", "Opposite Lane", "Cross Road", "Approaches Intersection", "Parked"]
emv_direction_options = ["Approaches from Behind", "As Lead Vehicle"]
ev_action = ["Go Straight", "Go Straight and Turn Left", "Go Straight and Turn Right", "Turn Left", "Turn Right"]
emv_action = ["Go Straight", "Go Straight and Turn Left", "Go Straight and Turn Right", "Turn Left", "Turn Right"]

# Function to handle the Start Simulation button click
def set_up_simulation():
    global scenario_info
    connect_to_carla()
    
    spawn_ego_vehicle()
    
    spawn_emergency_vehicle()
    
    set_spectator()

    scenario_info = default_values.copy()

    road_type_cb.set(default_values["road_type"])
    ego_vehicle_position_cb.set(default_values["ego_vehicle_position"])
    emv_position_cb.set(default_values["emv_position"])
    emv_direction_cb.set(default_values["emv_direction"])
    ego_action_cb.set(default_values["ev_action"])
    emv_action_cb.set(default_values["emv_action"]) 
        
# Function to handle value changes in comboboxes
def on_combobox_ego_position_change(event, combobox_name):
    current_value = event.widget.get()  
    if current_value != scenario_info[combobox_name]:
        scenario_info[combobox_name] = current_value
        
        if scenario_info[combobox_name] == "Traffic Lane":
            change_ego_vehicle_spawn_point(41)
        elif  scenario_info[combobox_name] == "Approaching Intersection":
            change_ego_vehicle_spawn_point(37)
        
# Function to handle value changes in comboboxes
def on_combobox_emv_position_change(event, combobox_name):
    current_value = event.widget.get()  
    if current_value != scenario_info[combobox_name]:
        scenario_info[combobox_name] = current_value
        
        if current_value == "Approaches Intersection":
            emv_direction_cb.set("")
        if current_value == "Parked":
            emv_direction_cb.set("")
            emv_action_cb.set("")
            
        map_scenario_for_motorway_same_lane_and_parallel_lane(scenario_info)
            
                    
# Function to handle value changes in comboboxes
def on_combobox_emv_direction_change(event, combobox_name):
    current_value = event.widget.get()
    if current_value != scenario_info[combobox_name]:
        scenario_info[combobox_name] = current_value
        
        map_scenario_for_motorway_same_lane_and_parallel_lane(scenario_info)

# Function to handle value changes in comboboxes
def on_combobox_ev_action_change(event, combobox_name):
    current_value = event.widget.get()
    if current_value != scenario_info[combobox_name]:
        scenario_info[combobox_name] = current_value

# Function to handle value changes in comboboxes
def on_combobox_emv_action_change(event, combobox_name):
    current_value = event.widget.get()
    if current_value != scenario_info[combobox_name]:
        scenario_info[combobox_name] = current_value
        
def start_simulation():
    ego_velocity = int(ego_velocity_sb.get())
    emv_velocity = int(emv_velocity_sb.get())
    log_safe_distance = int(long_safe_distance_sb.get())
    lat_safe_distance = int(lat_safe_distance_sb.get())
    
    threading.Thread(target=monitor_odd, args=[log_safe_distance, lat_safe_distance]).start()
    threading.Thread(target=activate_autopilot, args=[ego_velocity, emv_velocity, scenario_info]).start()
    
# Initialize the main window and GUI setup
root = tk.Tk()
root.title("ScenarioInfoManager")
root.geometry("600x700")  # Set the window size

# Define a larger font
large_font = ("Helvetica", 14)

# Create a style object
style = ttk.Style()
style.configure('TButton', font=large_font)

# Create a Frame to hold the buttons
button_frame_ev = tk.Frame(root)
button_frame_ev.grid(row=4, column=1, padx=10, pady=10)

button_frame_emv = tk.Frame(root)
button_frame_emv.grid(row=5, column=1, padx=10, pady=10)

# Create and place the widgets
ttk.Label(root, text="Road Type", font=large_font).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
road_type_cb = ttk.Combobox(root, values=road_type_options, state="readonly", font=large_font)
road_type_cb.set(default_values["road_type"])
road_type_cb.grid(row=0, column=1, padx=20, pady=10)

ttk.Label(root, text="Ego Vehicle Position", font=large_font).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
ego_vehicle_position_cb = ttk.Combobox(root, values=ego_vehicle_position_options, state="readonly", font=large_font)
ego_vehicle_position_cb.set(default_values["ego_vehicle_position"])
ego_vehicle_position_cb.grid(row=1, column=1, padx=20, pady=10)
ego_vehicle_position_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_ego_position_change(event, "ego_vehicle_position"))

ttk.Label(root, text="Emergency Vehicle Position", font=large_font).grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
emv_position_cb = ttk.Combobox(root, values=emv_position_options, state="readonly", font=large_font)
emv_position_cb.set(default_values["emv_position"])
emv_position_cb.grid(row=2, column=1, padx=20, pady=10)
emv_position_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_emv_position_change(event, "emv_position"))

ttk.Label(root, text="Emergency Vehicle Role", font=large_font).grid(row=3, column=0, padx=20, pady=10, sticky=tk.W)
emv_direction_cb = ttk.Combobox(root, values=emv_direction_options, state="readonly", font=large_font)
emv_direction_cb.set(default_values["emv_direction"])
emv_direction_cb.grid(row=3, column=1, padx=20, pady=10)
emv_direction_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_emv_direction_change(event, "emv_direction"))

ttk.Label(root, text="Change EV Position", font=large_font).grid(row=4, column=0, padx=20, pady=10, sticky=tk.W)
change_ev_position_btn = ttk.Button(button_frame_ev, text="Move +5m", command=lambda: change_vehicle_position(5, "ego", "forward"), style='TButton')
change_ev_position_bw_btn = ttk.Button(button_frame_ev, text="Move -5m", command=lambda: change_vehicle_position(5, "ego", "backward"), style='TButton')
change_ev_position_btn.pack(side='left', padx=1)
change_ev_position_bw_btn.pack(side='left', padx=1)

ttk.Label(root, text="Change EMV Position", font=large_font).grid(row=5, column=0, padx=20, pady=10, sticky=tk.W)
change_emv_position_btn = ttk.Button(button_frame_emv, text="Move +5m", command=lambda: change_vehicle_position(5, "emv", "forward"), style='TButton')
change_emv_position_bw_btn = ttk.Button(button_frame_emv, text="Move -5m", command=lambda: change_vehicle_position(5, "emv", "backward"), style='TButton')
change_emv_position_btn.pack(side='left', padx=1)
change_emv_position_bw_btn.pack(side='left', padx=1)

ttk.Label(root, text="EV Travel Direction", font=large_font).grid(row=6, column=0, padx=20, pady=10, sticky=tk.W)
ego_action_cb = ttk.Combobox(root, values=ev_action, state="readonly", font=large_font)
ego_action_cb.set(default_values["ev_action"])
ego_action_cb.grid(row=6, column=1, padx=20, pady=10)
ego_action_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_ev_action_change(event, "ev_action"))

ttk.Label(root, text="EMV Travel Direction", font=large_font).grid(row=7, column=0, padx=20, pady=10, sticky=tk.W)
emv_action_cb = ttk.Combobox(root, values=emv_action, state="readonly", font=large_font)
emv_action_cb.set(default_values["emv_action"])
emv_action_cb.grid(row=7, column=1, padx=20, pady=10)
emv_action_cb.bind("<<ComboboxSelected>>", lambda event: on_combobox_emv_action_change(event, "emv_action"))

ttk.Label(root, text="Set Ego Velocity (km/h)", font=large_font).grid(row=8, column=0, padx=20, pady=10, sticky=tk.W)
ego_velocity_sb = tk.Spinbox(root, from_=0, to=100, increment=10, font=large_font)
ego_velocity_sb.grid(row=8, column=1, padx=20, pady=10)

ttk.Label(root, text="Set EMV Velocity (km/h)", font=large_font).grid(row=9, column=0, padx=20, pady=10, sticky=tk.W)
emv_velocity_sb = tk.Spinbox(root, from_=0, to=100, increment=10, font=large_font)
emv_velocity_sb.grid(row=9, column=1, padx=20, pady=10)

ttk.Label(root, text="Safe Longitudinal Distance (m)", font=large_font).grid(row=10, column=0, padx=20, pady=10, sticky=tk.W)
long_safe_distance_sb = tk.Spinbox(root, from_=0, to=200, increment=1, font=large_font)
long_safe_distance_sb.grid(row=10, column=1, padx=20, pady=10)

ttk.Label(root, text="Safe Lateral Distance (m)", font=large_font).grid(row=11, column=0, padx=20, pady=10, sticky=tk.W)
lat_safe_distance_sb = tk.Spinbox(root, from_=0, to=200, increment=1, font=large_font)
lat_safe_distance_sb.grid(row=11, column=1, padx=20, pady=10)

setup_button = ttk.Button(root, text="Setup", command=set_up_simulation, style='TButton')
setup_button.grid(row=12, column=0, padx=5, pady=20)

start_button = ttk.Button(root, text="Start", command=start_simulation, style='TButton')
start_button.grid(row=12, column=0, columnspan=2, padx=5, pady=20)

stop_button = ttk.Button(root, text="Stop", command=stop_simulation, style='TButton')
stop_button.grid(row=12, column=0, columnspan=2, padx=5, pady=20)
stop_button.grid(row=12, column=1, padx=5, pady=10)
# Start the main event loop
root.mainloop()
