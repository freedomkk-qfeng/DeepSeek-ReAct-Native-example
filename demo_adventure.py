from deepseek_agent import DeepSeekAgent
from config import API_CONFIG

# --- Game Engine ---
class GameState:
    def __init__(self):
        self.current_room = "start_room"
        self.inventory = []
        self.rooms = {
            "start_room": {
                "description": "你在一间昏暗的石室里。空气中弥漫着灰尘的味道。",
                "exits": {"north": "hallway"},
                "items": []
            },
            "hallway": {
                "description": "你站在一条长长的走廊上。西边有一扇巨大的铁门，看起来锁得很紧。",
                "exits": {"south": "start_room", "east": "storage_room", "west": "exit_room"},
                "items": [],
                "locked_exits": ["west"]
            },
            "storage_room": {
                "description": "这是一个杂乱的储藏室，堆满了旧箱子。",
                "exits": {"west": "hallway"},
                "items": ["key"]
            },
            "exit_room": {
                "description": "你成功逃出来了！阳光洒在你的脸上。恭喜通关！",
                "exits": {},
                "items": []
            }
        }

    def get_map(self):
        hallway = self.rooms["hallway"]
        west_door_symbol = "---"
        if "locked_exits" in hallway and "west" in hallway["locked_exits"]:
            west_door_symbol = "-X-" # Locked state
        
        # Helper to add * marker
        def get_label(name, room_id):
            base = f"[{name}]"
            if self.current_room == room_id:
                return base + "*"
            return base
            
        l_exit = get_label("Exit", "exit_room")
        l_hallway = get_label("Hallway", "hallway")
        l_storage = get_label("Storage", "storage_room")
        l_start = get_label("Start", "start_room")
        
        # Construct the map lines dynamically to ensure alignment
        # Layout:
        #       [Exit] -X- [Hallway] --- [Storage]
        #                     |
        #                  [Start]
        
        # 1. Top Line
        # Fixed padding for left side
        prefix = "      "
        # Left part: prefix + [Exit] + " " + symbol + " "
        left_part = f"{prefix}{l_exit} {west_door_symbol} "
        
        top_line = f"{left_part}{l_hallway} --- {l_storage}"
        
        # 2. Vertical Line (Pipe)
        # The pipe should be centered under [Hallway]
        # Start index of Hallway is len(left_part)
        hallway_center_idx = len(left_part) + len(l_hallway) // 2
        vertical_line = " " * hallway_center_idx + "|"
        
        # 3. Bottom Line ([Start])
        # [Start] should be centered under the pipe
        start_start_idx = hallway_center_idx - len(l_start) // 2
        bottom_line = " " * start_start_idx + l_start
        
        return f"\nMap:\n{top_line}\n{vertical_line}\n{bottom_line}\n(* indicates your current location, -X- indicates a locked door)\n"

    def look(self):
        room = self.rooms[self.current_room]
        desc = room["description"]
        items_desc = f" 这里有: {', '.join(room['items'])}." if room["items"] else ""
        exits_desc = f" 出口有: {', '.join(room['exits'].keys())}."
        return f"{desc}{items_desc}{exits_desc} (当前持有物品: {', '.join(self.inventory) if self.inventory else '无'})\n{self.get_map()}"

    def move(self, direction):
        room = self.rooms[self.current_room]
        if direction in room["exits"]:
            if "locked_exits" in room and direction in room["locked_exits"]:
                return f"无法向 {direction} 移动，门锁着。你需要先解锁 (unlock)。"
            
            next_room_id = room["exits"][direction]
            self.current_room = next_room_id
            
            if next_room_id == "exit_room":
                return self.rooms[next_room_id]["description"] + "\n" + self.get_map()
            return f"你向 {direction} 移动。\n{self.look()}"
        else:
            return "那个方向没有路。"

    def take(self, item):
        room = self.rooms[self.current_room]
        if item in room["items"]:
            room["items"].remove(item)
            self.inventory.append(item)
            return f"你捡起了 {item}。"
        else:
            return f"这里没有 {item}。"

    def unlock(self, direction):
        room = self.rooms[self.current_room]
        if "locked_exits" in room and direction in room["locked_exits"]:
            if "key" in self.inventory:
                room["locked_exits"].remove(direction)
                return f"你用钥匙打开了 {direction} 边的门！"
            else:
                return "你没有钥匙，打不开门。"
        else:
            return "那个方向没有锁着的门，或者根本没有门。"

# --- Tool Definitions ---
game = GameState()

tools = [
    {
        "type": "function",
        "function": {
            "name": "look",
            "description": "Observes the current environment, showing room description, items, and exits.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move",
            "description": "Moves in a specified direction.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "direction": {"type": "string", "enum": ["north", "south", "east", "west"], "description": "The direction to move"}
                }, 
                "required": ["direction"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take",
            "description": "Picks up an item from the current room.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "item": {"type": "string", "description": "The name of the item to pick up"}
                }, 
                "required": ["item"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unlock",
            "description": "Attempts to unlock a door in a specified direction.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "direction": {"type": "string", "enum": ["north", "south", "east", "west"], "description": "The direction of the door to unlock"}
                }, 
                "required": ["direction"]
            }
        }
    }
]

TOOL_MAP = {
    "look": game.look,
    "move": game.move,
    "take": game.take,
    "unlock": game.unlock
}

# --- Main Program ---
if __name__ == "__main__":
    agent = DeepSeekAgent(**API_CONFIG)
    
    print(f"\n{'='*20} Starting Text Adventure Game {'='*20}")
    print("Goal: Escape from this place!")
    
    messages = [
        {"role": "user", "content": "我被困在一个陌生的地方。请帮我逃出去。你需要先观察环境 (look)，然后探索周围。如果遇到锁着的门，试着找找钥匙。"}
    ]
    
    agent.run(messages, tools, TOOL_MAP, max_turns=20)
