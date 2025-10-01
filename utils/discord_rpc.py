# utils/discord_rpc.py
from pypresence import Presence
import time

def start_discord_rpc(game_name: str):
    try:
        RPC = Presence("TU_CLIENT_ID")  # Registra tu app en Discord Dev
        RPC.connect()
        RPC.update(
            state=f"Jugando a {game_name}",
            large_image="multiverse_logo",
            start=time.time()
        )
        return RPC
    except:
        return None