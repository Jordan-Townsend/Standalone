#!/usr/bin/env python3
"""
Meshtastic Command Center - Backend Server
WebSocket server that bridges Meshtastic hardware with web interface
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
import signal
import sys

import websockets
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MeshtasticServer:
    """WebSocket server that connects Meshtastic device to web clients"""
    
    def __init__(self, port='/dev/ttyACM0', ws_host='localhost', ws_port=8765):
        self.port = port
        self.ws_host = ws_host
        self.ws_port = ws_port
        
        self.interface = None
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Data storage
        self.nodes = {}
        self.messages = []
        self.stats = {
            'total_messages': 0,
            'total_nodes': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # Discovery state
        self.discovery_active = False
        self.pending_pings = set()
        
    async def start(self):
        """Start the server and connect to Meshtastic device"""
        logger.info("Starting Meshtastic Command Center Server...")
        
        # Connect to Meshtastic device
        try:
            logger.info(f"Connecting to Meshtastic device on {self.port}...")
            self.interface = meshtastic.serial_interface.SerialInterface(self.port)
            
            # Subscribe to Meshtastic events
            pub.subscribe(self.on_receive, "meshtastic.receive")
            pub.subscribe(self.on_connection, "meshtastic.connection.established")
            
            logger.info("✓ Connected to Meshtastic device")
            
            # Wait for connection to stabilize
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to connect to Meshtastic device: {e}")
            logger.info("Server will run in demo mode")
        
        # Start WebSocket server
        logger.info(f"Starting WebSocket server on {self.ws_host}:{self.ws_port}")
        async with websockets.serve(self.handle_client, self.ws_host, self.ws_port):
            logger.info("✓ WebSocket server running")
            logger.info(f"Open http://{self.ws_host}:{self.ws_port} in your browser")
            
            # Run forever
            await asyncio.Future()
    
    def on_connection(self, interface, topic=None):
        """Handle Meshtastic connection established"""
        logger.info("Meshtastic connection established")
        asyncio.create_task(self.broadcast_to_clients({
            'type': 'system_message',
            'from': 'System',
            'text': '✓ Meshtastic device connected',
            'timestamp': datetime.now().isoformat()
        }))
    
    def on_receive(self, packet, interface=None):
        """Handle incoming Meshtastic packets"""
        try:
            if 'decoded' not in packet:
                return
            
            from_id = packet.get('fromId', 'unknown')
            decoded = packet['decoded']
            
            # Update or create node
            if from_id not in self.nodes:
                self.nodes[from_id] = {
                    'id': from_id,
                    'name': from_id,
                    'first_seen': datetime.now().isoformat(),
                    'last_seen': datetime.now().isoformat(),
                    'packets': 0
                }
                logger.info(f"New node discovered: {from_id}")
            
            node = self.nodes[from_id]
            node['last_seen'] = datetime.now().isoformat()
            node['packets'] += 1
            
            # Update metrics
            if 'rxSnr' in packet:
                node['snr'] = packet['rxSnr']
            if 'rxRssi' in packet:
                node['rssi'] = packet['rxRssi']
            if 'hopLimit' in packet and 'hopStart' in packet:
                node['hops'] = packet['hopStart'] - packet['hopLimit']
            
            # Handle different packet types
            portnum = decoded.get('portnum', '')
            
            if portnum == 'TEXT_MESSAGE_APP':
                text = decoded.get('text', '')
                self.handle_text_message(from_id, text)
            
            elif portnum == 'POSITION_APP':
                self.handle_position(from_id, decoded.get('position', {}))
            
            elif portnum == 'NODEINFO_APP':
                self.handle_nodeinfo(from_id, decoded.get('user', {}))
            
            elif portnum == 'TELEMETRY_APP':
                self.handle_telemetry(from_id, decoded.get('telemetry', {}))
            
            # Broadcast node update to all clients
            asyncio.create_task(self.broadcast_to_clients({
                'type': 'node_update',
                'node': node
            }))
            
            # Update stats
            self.stats['total_nodes'] = len(self.nodes)
            asyncio.create_task(self.broadcast_to_clients({
                'type': 'stats_update',
                'stats': self.stats
            }))
            
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
    
    def handle_text_message(self, from_id, text):
        """Handle text message"""
        node = self.nodes.get(from_id, {})
        name = node.get('name', from_id)
        
        message = {
            'from': name,
            'from_id': from_id,
            'text': text,
            'timestamp': datetime.now().isoformat()
        }
        
        self.messages.append(message)
        self.stats['total_messages'] += 1
        
        logger.info(f"Message from {name}: {text}")
        
        asyncio.create_task(self.broadcast_to_clients({
            'type': 'message',
            **message
        }))
    
    def handle_position(self, from_id, position):
        """Handle position update"""
        if from_id in self.nodes:
            self.nodes[from_id]['position'] = {
                'latitude': position.get('latitude'),
                'longitude': position.get('longitude'),
                'altitude': position.get('altitude')
            }
            
            logger.info(f"Position update from {from_id}")
            
            asyncio.create_task(self.broadcast_to_clients({
                'type': 'node_update',
                'node': self.nodes[from_id]
            }))
    
    def handle_nodeinfo(self, from_id, user):
        """Handle node info update"""
        if from_id in self.nodes:
            self.nodes[from_id]['name'] = user.get('longName', from_id)
            self.nodes[from_id]['short_name'] = user.get('shortName', '????')
            self.nodes[from_id]['hw_model'] = user.get('hwModel', 'unknown')
            
            logger.info(f"Node info: {user.get('longName', from_id)}")
            
            asyncio.create_task(self.broadcast_to_clients({
                'type': 'node_update',
                'node': self.nodes[from_id]
            }))
    
    def handle_telemetry(self, from_id, telemetry):
        """Handle telemetry update"""
        if from_id in self.nodes:
            if 'deviceMetrics' in telemetry:
                metrics = telemetry['deviceMetrics']
                self.nodes[from_id]['battery'] = metrics.get('batteryLevel')
                self.nodes[from_id]['voltage'] = metrics.get('voltage')
                self.nodes[from_id]['channel_utilization'] = metrics.get('channelUtilization')
                self.nodes[from_id]['air_util_tx'] = metrics.get('airUtilTx')
            
            asyncio.create_task(self.broadcast_to_clients({
                'type': 'node_update',
                'node': self.nodes[from_id]
            }))
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        logger.info(f"Client connected from {websocket.remote_address}")
        self.connected_clients.add(websocket)
        
        try:
            # Send initial state to new client
            await websocket.send(json.dumps({
                'type': 'init',
                'nodes': list(self.nodes.values()),
                'messages': self.messages[-50:],  # Last 50 messages
                'stats': self.stats
            }))
            
            # Handle client messages
            async for message in websocket:
                await self.handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected from {websocket.remote_address}")
        finally:
            self.connected_clients.remove(websocket)
    
    async def handle_client_message(self, websocket, message):
        """Handle incoming messages from web client"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'start_discovery':
                await self.start_discovery()
            
            elif command == 'ping_all':
                await self.ping_all_nodes()
            
            elif command == 'send_message':
                await self.send_message(
                    data.get('text', ''),
                    data.get('target', 'broadcast')
                )
            
            elif command == 'send_broadcast':
                await self.send_broadcast(
                    data.get('text', ''),
                    data.get('message_type', 'text')
                )
            
            elif command == 'connect_device':
                await self.connect_device(
                    data.get('port', '/dev/ttyACM0'),
                    data.get('region', 'US')
                )
            
            elif command == 'export_data':
                await websocket.send(json.dumps({
                    'type': 'export_data',
                    'data': {
                        'nodes': list(self.nodes.values()),
                        'messages': self.messages,
                        'stats': self.stats,
                        'timestamp': datetime.now().isoformat()
                    }
                }))
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
    
    async def start_discovery(self):
        """Start cascade discovery process"""
        logger.info("Starting cascade discovery...")
        self.discovery_active = True
        
        await self.broadcast_to_clients({
            'type': 'system_message',
            'from': 'System',
            'text': '🔍 Starting cascade discovery...',
            'timestamp': datetime.now().isoformat()
        })
        
        if self.interface:
            try:
                # Send initial broadcast ping
                self.interface.sendText("DISCOVERY_PING", channelIndex=0)
                
                # Wait and send targeted pings to discovered nodes
                await asyncio.sleep(5)
                
                for node_id in self.nodes.keys():
                    try:
                        self.interface.sendData(
                            b"",
                            destinationId=node_id,
                            portNum=meshtastic.portnums_pb2.ROUTING_APP,
                            wantAck=True,
                            wantResponse=True
                        )
                        await asyncio.sleep(2)
                    except Exception as e:
                        logger.error(f"Error pinging {node_id}: {e}")
                
                await self.broadcast_to_clients({
                    'type': 'system_message',
                    'from': 'System',
                    'text': f'✅ Discovery complete! Found {len(self.nodes)} nodes.',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Discovery error: {e}")
                await self.broadcast_to_clients({
                    'type': 'system_message',
                    'from': 'System',
                    'text': f'❌ Discovery error: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                })
        else:
            # Demo mode - simulate discovery
            await self.simulate_discovery()
        
        self.discovery_active = False
    
    async def simulate_discovery(self):
        """Simulate discovery in demo mode"""
        demo_nodes = [
            {
                'id': '!a1b2c3d4',
                'name': 'Base Station',
                'snr': 8.5,
                'rssi': -85,
                'hops': 0,
                'battery': 95,
                'position': {'latitude': 45.4981, 'longitude': -122.4404}
            },
            {
                'id': '!e5f6g7h8',
                'name': 'Node Alpha',
                'snr': 4.2,
                'rssi': -105,
                'hops': 1,
                'battery': 78,
                'position': {'latitude': 45.5081, 'longitude': -122.4504}
            },
            {
                'id': '!i9j0k1l2',
                'name': 'Node Beta',
                'snr': 6.8,
                'rssi': -92,
                'hops': 1,
                'battery': 88,
                'position': {'latitude': 45.4881, 'longitude': -122.4304}
            }
        ]
        
        for node in demo_nodes:
            await asyncio.sleep(1)
            node['first_seen'] = datetime.now().isoformat()
            node['last_seen'] = datetime.now().isoformat()
            node['packets'] = 1
            
            self.nodes[node['id']] = node
            self.stats['total_nodes'] = len(self.nodes)
            
            await self.broadcast_to_clients({
                'type': 'node_update',
                'node': node
            })
    
    async def ping_all_nodes(self):
        """Ping all discovered nodes"""
        logger.info("Pinging all nodes...")
        
        await self.broadcast_to_clients({
            'type': 'system_message',
            'from': 'System',
            'text': f'📡 Pinging {len(self.nodes)} nodes...',
            'timestamp': datetime.now().isoformat()
        })
        
        if self.interface:
            for node_id in self.nodes.keys():
                try:
                    self.interface.sendText("PING", destinationId=node_id, wantAck=True)
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error pinging {node_id}: {e}")
        
        await asyncio.sleep(2)
        await self.broadcast_to_clients({
            'type': 'system_message',
            'from': 'System',
            'text': f'✅ Ping complete',
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_message(self, text, target='broadcast'):
        """Send a text message"""
        if not self.interface:
            logger.warning("No Meshtastic interface available")
            return
        
        try:
            if target == 'broadcast':
                self.interface.sendText(text, channelIndex=0)
            else:
                self.interface.sendText(text, destinationId=target, wantAck=True)
            
            logger.info(f"Sent message: {text}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def send_broadcast(self, text, message_type='text'):
        """Send a broadcast message to all nodes"""
        logger.info(f"Broadcasting {message_type}: {text}")
        
        await self.broadcast_to_clients({
            'type': 'system_message',
            'from': 'System',
            'text': f'📢 Broadcasting: {text}',
            'timestamp': datetime.now().isoformat()
        })
        
        if self.interface:
            try:
                # Send to broadcast channel
                self.interface.sendText(text, channelIndex=0)
                
                # Also send directly to each known node
                for node_id in self.nodes.keys():
                    try:
                        self.interface.sendText(text, destinationId=node_id, wantAck=True)
                        await asyncio.sleep(1)
                    except Exception as e:
                        logger.error(f"Error sending to {node_id}: {e}")
                
                await self.broadcast_to_clients({
                    'type': 'system_message',
                    'from': 'System',
                    'text': '✅ Broadcast complete',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
    
    async def connect_device(self, port, region):
        """Connect to Meshtastic device"""
        logger.info(f"Connecting to device on {port} (Region: {region})")
        
        try:
            if self.interface:
                self.interface.close()
            
            self.interface = meshtastic.serial_interface.SerialInterface(port)
            
            await self.broadcast_to_clients({
                'type': 'system_message',
                'from': 'System',
                'text': f'✅ Connected to {port}',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            await self.broadcast_to_clients({
                'type': 'system_message',
                'from': 'System',
                'text': f'❌ Connection failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            })
    
    async def broadcast_to_clients(self, data):
        """Broadcast data to all connected clients"""
        if not self.connected_clients:
            return
        
        message = json.dumps(data)
        
        # Create tasks for sending to all clients
        tasks = [client.send(message) for client in self.connected_clients]
        
        # Wait for all sends to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def cleanup(self):
        """Cleanup on shutdown"""
        logger.info("Shutting down...")
        
        if self.interface:
            try:
                self.interface.close()
                logger.info("✓ Meshtastic interface closed")
            except Exception as e:
                logger.error(f"Error closing interface: {e}")


async def main():
    """Main entry point"""
    server = MeshtasticServer(
        port='/dev/ttyACM0',
        ws_host='localhost',
        ws_port=8765
    )
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        server.cleanup()
        loop.stop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        server.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
