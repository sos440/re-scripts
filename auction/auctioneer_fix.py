import json
import os
import re
from datetime import datetime
import random
from collections import OrderedDict

# Configurable Settings
TRIGGER_WORDS = {
    'sold': 'SOLD!',
    'not_sold': 'NOT SOLD!'
}

MESSAGE_COLORS = {
    'announcement': 68, 
    'bid': 66,      
    'error': 33,    
    'success': 90,   
    'reserve': 53   
}

OPENING_PHRASES = [
    "First item up for bid is...", 
    "Next item up is...",
    "Next item up for bid is...",
    "Moving on to...",
    "Now we have...",
    "Coming up next...",
    "Ladies and gentlemen, next we have..."
]

FINAL_ANNOUNCEMENTS = {
    'sold': "{winner} wins {title} for {amount} gold!",
    'not_sold': "Item has been withdrawn.",
    'reserve_not_met': "Reserve not met. Item withdrawn."
}

MESSAGE_DELAYS = {
    'after_opening': 1000,  
    'after_title': 2000,   
    'after_desc': 2000,   
    'after_bid': 1000,   
    'after_final': 1000  
}

# Bid parsing patterns
BID_PATTERNS = [
    (r'(-?\d+\.?\d*)[kK]', lambda x: int(float(x) * 1000)),              # 1k, 1.5k, -1k
    (r'(-?\d+\.?\d*)[mM]', lambda x: int(float(x) * 1000000)),           # 1m, 1.5m, -1m
    (r'(-?\d+(?:[,\.]\d{3})+)', lambda x: int(float(x.replace(',', '')))), # 1,000,000 or -1,000,000
    (r'(-?\d+)', lambda x: int(x))                                        # Plain numbers and negatives
]

def load_auction_database():
    db_path = os.path.join(Misc.CurrentScriptDirectory(), 'auction_database.json')
    try:
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                data = f.read().strip()
                if data:
                    return json.loads(data)
    except Exception as e:
        Misc.SendMessage(f"Error loading database: {str(e)}", MESSAGE_COLORS['error'])
    return None

def save_auction_database(database):
    db_path = os.path.join(Misc.CurrentScriptDirectory(), 'auction_database.json')
    try:
        # Convert to OrderedDict to maintain field order
        ordered_db = {"auctions": []}
        for auction in database['auctions']:
            ordered_auction = OrderedDict([
                ('id', auction['id']),
                ('seller', auction['seller']),
                ('title', auction['title']),
                ('description', auction['description']),
                ('opening_bid', auction['opening_bid']),
                ('reserve_price', auction['reserve_price']),
                ('status', auction['status']),
                ('date', auction['date']),
                ('items', auction['items']),
                ('highest_bid', auction.get('highest_bid')),
                ('bidders', auction.get('bidders', []))
            ])
            ordered_db['auctions'].append(ordered_auction)
            
        with open(db_path, 'w') as f:
            json.dump(ordered_db, f, indent=4)
        return True
    except Exception as e:
        Misc.SendMessage(f"Error saving database: {str(e)}", MESSAGE_COLORS['error'])
        return False

def find_auction_by_item(database, item_serial):
    for auction in database['auctions']:
        for item in auction['items']:
            if int(item['serial']) == int(item_serial):
                return auction
    return None

def parse_bid_amount(text):
    text = text.strip()
    for pattern, converter in BID_PATTERNS:
        match = re.search(pattern, text)
        if match:
            try:
                return converter(match.group(1))
            except ValueError:
                return None
    return None

def is_player_in_range(mobile, range_tiles=12):
    """Check if a player is within range and only validate once per bid."""
    if not mobile:
        return False
    try:
        return Player.DistanceTo(mobile) <= range_tiles
    except:
        return False
        
def find_player_by_name(name):
    """Find a player by name with proper name matching."""
    name = name.lower().strip()
    filter = Mobiles.Filter()
    filter.Enabled = True
    for mobile in Mobiles.ApplyFilter(filter):
        if mobile.Name and mobile.Name.lower().strip() == name:
            return mobile
    return None
    
def get_opening_phrase(database):
    for auction in database['auctions']:
        if auction['status'] in ['sold', 'not sold']:
            return random.choice(OPENING_PHRASES[1:])  # Skip "First item" phrase
    return OPENING_PHRASES[0]  # Use "First item" phrase

def announce_auction(auction):
    # Opening
    opening = get_opening_phrase(database)
    Player.ChatSay(MESSAGE_COLORS['announcement'], opening)
    Misc.Pause(MESSAGE_DELAYS['after_opening'])
    
    # Title
    Player.ChatSay(MESSAGE_COLORS['announcement'], auction['title'] or "Untitled Item")
    Misc.Pause(MESSAGE_DELAYS['after_title'])
    
    # Description
    if auction['description']:
        Player.ChatSay(MESSAGE_COLORS['announcement'], auction['description'])
        Misc.Pause(MESSAGE_DELAYS['after_desc'])
    
    # Starting bid
    if auction['opening_bid'] == "TBD":
        bid_msg = "Opening bid to be determined."
    else:
        bid_msg = f"Opening bid is {auction['opening_bid']} gold."
    Player.ChatSay(MESSAGE_COLORS['announcement'], bid_msg)
    
    # Show reserve price to auctioneer if set
    if auction['reserve_price']:
        Misc.SendMessage(f"Reserve price is set to: {auction['reserve_price']:,} gold", MESSAGE_COLORS['reserve'])
    
    # Clear journal after announcements
    Journal.Clear()

def remove_bid(auction, bidder_name):
    if not auction.get('bidders'):
        Misc.SendMessage(f"No bids to remove for {bidder_name}", MESSAGE_COLORS['error'])
        return False
        
    # Find the most recent bid from this bidder
    found = False
    for i in range(len(auction['bidders']) - 1, -1, -1):
        if auction['bidders'][i]['name'].lower() == bidder_name.lower():
            removed_bid = auction['bidders'].pop(i)
            found = True
            break
            
    if not found:
        Misc.SendMessage(f"No bids found for {bidder_name}", MESSAGE_COLORS['error'])
        return False
        
    # Update highest bid
    if auction['bidders']:
        auction['highest_bid'] = auction['bidders'][-1]['amount']
        Player.ChatSay(MESSAGE_COLORS['announcement'], 
            f"Removed {bidder_name}'s bid of {removed_bid['amount']:,} gold. Current high bid: {auction['highest_bid']:,} gold by {auction['bidders'][-1]['name']}")
    else:
        auction['highest_bid'] = 0
        Player.ChatSay(MESSAGE_COLORS['announcement'], 
            f"Removed {bidder_name}'s bid of {removed_bid['amount']:,} gold. No current bids.")
    
    # Save changes immediately
    save_auction_database(database)
    return True

def process_bid(auction, bidder_name, bid_amount):
    # Process bid removal (negative bids)
    if bid_amount < 0:
        # Get recent journal entries
        entries = Journal.GetJournalEntry(datetime.now().timestamp() - 10)  # Get entries from last 10 seconds
        
        # Look for the command in recent entries
        for entry in entries:
            if (entry.Serial == Player.Serial and 
                Player.Name in entry.Name and  # Check if player name is in entry name
                bidder_name in entry.Text and 
                str(bid_amount) in entry.Text):  # Check for the actual bid amount
                # Command confirmed from auctioneer
                bids_to_remove = abs(bid_amount)
                removed = 0
                while removed < bids_to_remove:
                    if remove_bid(auction, bidder_name):
                        removed += 1
                    else:
                        break
                return True
                
        # If we get here, command was not from auctioneer
        Misc.SendMessage("Only the auctioneer can remove bids", MESSAGE_COLORS['error'])
        return False
    
    # Initialize bid tracking if not present
    if 'highest_bid' not in auction or auction['highest_bid'] is None:
        auction['highest_bid'] = 0
    if 'bidders' not in auction or auction['bidders'] is None:
        auction['bidders'] = []
        
    # Convert highest_bid to int for comparison
    current_highest = int(auction['highest_bid'])
        
    # Validate bid amount
    if bid_amount <= current_highest:
        return False
    
    # If there's an opening bid, check against it
    if auction['opening_bid'] != "TBD" and bid_amount < int(auction['opening_bid']):
        return False
        
    auction['highest_bid'] = bid_amount
    auction['bidders'].append({
        'name': bidder_name,
        'amount': bid_amount,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Announce new high bid
    bid_msg = f"{bidder_name} bids {bid_amount:,} gold!"
    Misc.Pause(MESSAGE_DELAYS['after_bid'])  
    Player.ChatSay(MESSAGE_COLORS['bid'], bid_msg)
    
    # Check reserve
    if auction['reserve_price'] and bid_amount >= auction['reserve_price']:
        Player.ChatSay(MESSAGE_COLORS['reserve'], "Reserve has been met!")
    
    return True

def handle_auction_end(auction, sold=True):
    if sold and auction.get('highest_bid', 0) > 0:
        winner = auction['bidders'][-1]['name']
        amount = auction['highest_bid']
        
        # Check if reserve was met
        if auction['reserve_price'] and amount < auction['reserve_price']:
            auction['status'] = 'not sold'
            msg = FINAL_ANNOUNCEMENTS['reserve_not_met']
            Misc.SendMessage(f"Reserve price of {auction['reserve_price']:,} gold was not met. Highest bid: {amount:,} gold", 
                MESSAGE_COLORS['reserve'])
        else:
            auction['status'] = 'sold'
            msg = FINAL_ANNOUNCEMENTS['sold'].format(
                winner=winner,
                title=auction['title'] or "Untitled Item",
                amount=f"{amount:,}"
            )
    else:
        auction['status'] = 'not sold'
        msg = FINAL_ANNOUNCEMENTS['not_sold']
    
    Player.ChatSay(MESSAGE_COLORS['announcement'], msg)
    Misc.Pause(MESSAGE_DELAYS['after_final'])
    return save_auction_database(database)

def run_auction():
    global database
    
    # Load database
    database = load_auction_database()
    if not database:
        Misc.SendMessage("Failed to load auction database!", MESSAGE_COLORS['error'])
        return
        
    # Get item selection
    Misc.SendMessage("Select item to auction:", MESSAGE_COLORS['announcement'])
    target = Target.PromptTarget()
    if target == -1:
        return
        
    # Find auction in database
    auction = find_auction_by_item(database, target)
    if not auction:
        Misc.SendMessage("Item not found in auction database!", MESSAGE_COLORS['error'])
        return
        
    if auction['status'] != 'pending':
        Misc.SendMessage("This item has already been auctioned!", MESSAGE_COLORS['error'])
        return
        
    # Clear journal and set timestamp
    Journal.Clear()
    Misc.Pause(100)
    
    # Announce auction and mark start time
    announce_auction(auction)
    timestamp = datetime.now().timestamp()  # Convert to Unix timestamp
    processed_entries = set()
    
    while True:
        entries = Journal.GetJournalEntry(timestamp)
        for entry in entries:
            # Create unique identifier for this entry
            entry_id = f"{entry.Serial}_{entry.Timestamp}_{entry.Text}"
            
            # Skip if we've already processed this entry
            if entry_id in processed_entries:
                continue
                
            # Add to processed entries
            processed_entries.add(entry_id)
            
            # Process auction end commands from auctioneer
            if entry.Serial == Player.Serial:
                if entry.Text.strip() == TRIGGER_WORDS['sold']:
                    handle_auction_end(auction, True)
                    return
                if entry.Text.strip() == TRIGGER_WORDS['not_sold']:
                    handle_auction_end(auction, False)
                    return
                
                # Handle manual bid entry or removal
                parts = entry.Text.split()
                if len(parts) >= 2:
                    # sos440's fix:
                    # Last part is bid amount, rest is bidder name
                    bidder_name = ' '.join(parts[:-1])
                    bid_text = parts[-1]
                    bid_amount = parse_bid_amount(bid_text)
                    
                    if bid_amount is not None:
                        if bid_amount < 0:
                            # Add cooldown for bid removal
                            Misc.Pause(1000)  # 1 second cooldown
                            process_bid(auction, bidder_name, bid_amount)
                        else:
                            player = find_player_by_name(bidder_name)
                            if player and is_player_in_range(player):
                                process_bid(auction, bidder_name, bid_amount)
            
            # Handle direct bids from players
            elif is_player_in_range(Mobiles.FindBySerial(entry.Serial)):
                bid_amount = parse_bid_amount(entry.Text)
                if bid_amount:
                    process_bid(auction, entry.Name, bid_amount)
        
        # Limit size of processed entries set
        if len(processed_entries) > 1000:
            processed_entries = set(list(processed_entries)[-500:])
            
        Misc.Pause(100)

def main():
    Misc.SendMessage("Starting Auction System", MESSAGE_COLORS['announcement'])
    run_auction()
    Misc.SendMessage("Auction Complete", MESSAGE_COLORS['announcement'])

if __name__ == "__main__":
    main()