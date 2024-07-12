import asyncio
import websockets
import json

# URL del websocket para LNbits
switchStr1 = "wss://demo.lnbits.com/api/v1/ws/W4dCMqavPLfSf4cDVW87UH"  # Player 1
switchStr2 = "wss://demo.lnbits.com/api/v1/ws/UjXNZhFTY3V4mCAbLVbYiG"  # Player 2


async def connect_to_websocket(switchStr, player, payment_received_callback):
    while True:
        try:
            print(f"Attempting to connect websocket for player {player} to {switchStr}")
            async with websockets.connect(switchStr, open_timeout=5, close_timeout=5) as websocket:
                print(f"Connected to websocket for player {player}")
                while True:
                    payload = await websocket.recv()
                    await process_message(payload, player, payment_received_callback)
        except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK, asyncio.TimeoutError) as e:
            print(f"Websocket connection closed or timeout for player {player}: {e}")
        except Exception as e:
            print(f"Unexpected error for player {player}: {e}")
        print(f"Reconnecting websocket for player {player} in 3 seconds...")
        await asyncio.sleep(3)

async def process_message(message, player, payment_received_callback):
        print(f"Player {player} received JSON data from socket: {message}")
        payment_received_callback(player)


async def main(payment_received_callback):
    await asyncio.gather(
        connect_to_websocket(switchStr1, 1, payment_received_callback),
        connect_to_websocket(switchStr2, 2, payment_received_callback),
    )

if __name__ == "__main__":
    def test_callback(player):
        print(f"Simulated payment received for player {player}")

    asyncio.run(main(test_callback))
