from System.Collections.Generic import List
import sys
import random

# Global variables for gump position
gump_x = 1200
gump_y = 30

# Script configurations with explicit display order
SCRIPTS = {
    'storage': {'file': 'auction item storage.py', 'label': 'Item Storage'},
    'auctioneer': {'file': 'auctioneer.py', 'label': 'Auctioneer'},
    'winnings': {'file': 'auction winner handler.py', 'label': 'Winnings'}
}

# Explicit display order
DISPLAY_ORDER = ['storage', 'auctioneer', 'winnings']

def toggle_script(script_id):
    """Toggle the specified script on or off."""
    try:
        script_file = SCRIPTS[script_id]['file']
        current_status = Misc.ScriptStatus(script_file)
        
        if current_status:
            Misc.ScriptStop(script_file)
            script_states[script_id] = False
            Player.HeadMessage(89, f"{SCRIPTS[script_id]['label']} Stopped")
        else:
            Misc.ScriptRun(script_file)
            script_states[script_id] = True
            Player.HeadMessage(68, f"{SCRIPTS[script_id]['label']} Started")
    except Exception as e:
        Player.HeadMessage(33, f"Error toggling {SCRIPTS[script_id]['label']}: {str(e)}")

def check_state_mismatch():
    """Check for mismatches between script states and their displayed state."""
    for script_id in SCRIPTS:
        current_status = Misc.ScriptStatus(SCRIPTS[script_id]['file'])
        if script_id in script_states and script_states[script_id] != current_status:
            script_states[script_id] = current_status
            return True
    return False

def initialize_states():
    """Initialize the script states dictionary."""
    global script_states
    if 'script_states' not in globals():
        script_states = {}
        for script_id in SCRIPTS:
            script_states[script_id] = Misc.ScriptStatus(SCRIPTS[script_id]['file'])
    return script_states

def create_control_gump():
    """Create the auction control gump."""
    global gump_x, gump_y
    
    # Initialize gump
    gump = Gumps.CreateGump()
    gump.gumpId = random.randint(100000000, 999999999)
    gump.serial = Player.Serial
    gump.x = gump_x
    gump.y = gump_y
    
    # Calculate dimensions
    width = 140
    height = len(SCRIPTS) * 25 + 15
    
    # Create background using specified gump ID 9270
    Gumps.AddBackground(gump, 0, 0, width, height, 9270)
    
    # Add buttons and labels in specified order
    for index, script_id in enumerate(DISPLAY_ORDER):
        script_info = SCRIPTS[script_id]
        y_pos = 10 + 25 * index
        button_id = DISPLAY_ORDER.index(script_id) + 1
        
        # Add button and label with color indicating status
        Gumps.AddButton(gump, 10, y_pos, 4005, 4006, button_id, 1, 0)
        Gumps.AddLabel(gump, 45, y_pos, 
                      script_states[script_id] and 68 or 89,  # Green when running, light blue when stopped
                      script_info['label'])
    
    return gump, gump.gumpId

def handle_gump_response(gump_id):
    """Handle gump button responses and updates."""
    global gump_x, gump_y
    
    try:
        refresh_timer = 0
        while True:
            gump = Gumps.GetGumpData(gump_id)
            if gump is None:
                break
            
            # Update stored position if gump was moved
            if hasattr(gump, 'x') and hasattr(gump, 'y'):
                gump_x = gump.x
                gump_y = gump.y
            
            # Check for button press
            if gump.buttonid != -1:
                script_index = gump.buttonid - 1
                if 0 <= script_index < len(DISPLAY_ORDER):
                    script_id = DISPLAY_ORDER[script_index]
                    toggle_script(script_id)
                
                # Refresh gump after toggle
                Gumps.CloseGump(gump_id)
                new_gump, new_id = create_control_gump()
                Gumps.SendGump(new_gump, gump_x, gump_y)
                gump_id = new_id
            
            # Check for state changes every second
            if refresh_timer >= 10:
                refresh_timer = 0
                if check_state_mismatch():
                    Gumps.CloseGump(gump_id)
                    new_gump, new_id = create_control_gump()
                    Gumps.SendGump(new_gump, gump_x, gump_y)
                    gump_id = new_id
            
            Misc.Pause(100)
            refresh_timer += 1
            
    except Exception as e:
        Player.HeadMessage(33, f"Error: {str(e)}")
        Misc.SendMessage(f"Error: {str(e)}")

def main():
    """Main execution function."""
    try:
        initialize_states()
        gump, gump_id = create_control_gump()
        Gumps.SendGump(gump, gump_x, gump_y)
        handle_gump_response(gump_id)
        
    except Exception as e:
        Player.HeadMessage(33, f"Fatal Error: {str(e)}")
        Misc.SendMessage(f"Fatal Error: {str(e)}")

# Start the script
if __name__ == '__main__':
    main()