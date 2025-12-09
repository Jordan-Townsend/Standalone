#!/usr/bin/env python3
"""
Meshtastic LilyGo T-Watch S3 Cascade Discovery Script
Discovers mesh nodes through cascading pings, tracks metrics, and broadcasts custom content
"""

import meshtastic
import meshtastic.serial_interface
from pubsub import pub
import time
import threading
import json
from datetime import datetime
from collections import defaultdict
import base64
import wave
import struct

class MeshCascadeDiscovery:
    def __init__(self, port='/dev/ttyACM0'):
        """Initialize the mesh discovery system"""
        self.interface = None
        self.port = port
        self.discovered_nodes = {}
        self.node_metrics = defaultdict(dict)
        self.pending_pings = set()
        self.discovery_complete = False
        self.lock = threading.Lock()
        
        # Configuration
        self.ping_interval = 30  # seconds between cascading pings
        self.max_discovery_time = 300  # 5 minutes max discovery time
        self.discovery_start_time = None
        
    def connect(self):
        """Connect to the Meshtastic device"""
        try:
            print(f"Connecting to Meshtastic device on {self.port}...")
            self.interface = meshtastic.serial_interface.SerialInterface(self.port)
            
            # Subscribe to message events
            pub.subscribe(self.on_receive, "meshtastic.receive")
            pub.subscribe(self.on_connection, "meshtastic.connection.established")
            
            print("✓ Connected successfully")
            time.sleep(2)  # Allow connection to stabilize
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        """Handle connection established event"""
        print("Connection established, ready to discover nodes")
    
    def on_receive(self, packet, interface=None):
        """Handle incoming messages"""
        try:
            if 'decoded' not in packet:
                return
            
            decoded = packet['decoded']
            from_id = packet.get('fromId', 'unknown')
            to_id = packet.get('toId', 'unknown')
            
            # Track node discovery
            with self.lock:
                if from_id not in self.discovered_nodes:
                    self.discovered_nodes[from_id] = {
                        'first_seen': datetime.now().isoformat(),
                        'last_seen': datetime.now().isoformat(),
                        'packet_count': 0,
                        'hops_away': packet.get('hopLimit', 0)
                    }
                    print(f"\n🎯 NEW NODE DISCOVERED: {from_id}")
                else:
                    self.discovered_nodes[from_id]['last_seen'] = datetime.now().isoformat()
                
                self.discovered_nodes[from_id]['packet_count'] += 1
            
            # Track metrics
            self.track_metrics(packet, from_id)
            
            # Handle different message types
            portnum = decoded.get('portnum', '')
            
            if portnum == 'TEXT_MESSAGE_APP':
                text = decoded.get('text', '')
                print(f"📨 Message from {from_id}: {text}")
            
            elif portnum == 'POSITION_APP':
                self.handle_position(packet, from_id)
            
            elif portnum == 'NODEINFO_APP':
                self.handle_nodeinfo(packet, from_id)
            
            elif portnum == 'TELEMETRY_APP':
                self.handle_telemetry(packet, from_id)
            
            elif portnum == 'ROUTING_APP':
                self.handle_routing_response(packet, from_id)
                
        except Exception as e:
            print(f"Error processing packet: {e}")
    
    def track_metrics(self, packet, node_id):
        """Track various metrics for each node"""
        with self.lock:
            metrics = self.node_metrics[node_id]
            
            # Signal metrics
            if 'rxSnr' in packet:
                if 'snr_values' not in metrics:
                    metrics['snr_values'] = []
                metrics['snr_values'].append(packet['rxSnr'])
                metrics['avg_snr'] = sum(metrics['snr_values']) / len(metrics['snr_values'])
            
            if 'rxRssi' in packet:
                if 'rssi_values' not in metrics:
                    metrics['rssi_values'] = []
                metrics['rssi_values'].append(packet['rxRssi'])
                metrics['avg_rssi'] = sum(metrics['rssi_values']) / len(metrics['rssi_values'])
            
            # Hop count
            if 'hopStart' in packet:
                metrics['max_hops'] = packet['hopStart']
                if 'hopLimit' in packet:
                    metrics['current_hop'] = packet['hopStart'] - packet['hopLimit']
    
    def handle_position(self, packet, node_id):
        """Handle position information"""
        decoded = packet.get('decoded', {})
        position = decoded.get('position', {})
        
        with self.lock:
            self.node_metrics[node_id]['position'] = {
                'latitude': position.get('latitude'),
                'longitude': position.get('longitude'),
                'altitude': position.get('altitude'),
                'time': datetime.now().isoformat()
            }
        
        print(f"📍 Position update from {node_id}")
    
    def handle_nodeinfo(self, packet, node_id):
        """Handle node information"""
        decoded = packet.get('decoded', {})
        user = decoded.get('user', {})
        
        with self.lock:
            self.node_metrics[node_id]['info'] = {
                'longName': user.get('longName', 'Unknown'),
                'shortName': user.get('shortName', '????'),
                'macaddr': user.get('macaddr', ''),
                'hwModel': user.get('hwModel', 'unknown')
            }
        
        long_name = user.get('longName', node_id)
        print(f"ℹ️  Node info: {long_name} ({node_id})")
    
    def handle_telemetry(self, packet, node_id):
        """Handle telemetry data"""
        decoded = packet.get('decoded', {})
        telemetry = decoded.get('telemetry', {})
        
        with self.lock:
            if 'deviceMetrics' in telemetry:
                self.node_metrics[node_id]['device_metrics'] = telemetry['deviceMetrics']
            
            if 'environmentMetrics' in telemetry:
                self.node_metrics[node_id]['environment_metrics'] = telemetry['environmentMetrics']
        
        print(f"📊 Telemetry from {node_id}")
    
    def handle_routing_response(self, packet, node_id):
        """Handle routing responses (ping acknowledgments)"""
        with self.lock:
            if node_id in self.pending_pings:
                self.pending_pings.remove(node_id)
                print(f"✓ Ping acknowledged by {node_id}")
    
    def send_ping(self, target_id=None):
        """Send a ping to discover nodes"""
        try:
            if target_id:
                print(f"📡 Sending targeted ping to {target_id}...")
                self.interface.sendData(
                    b"",
                    destinationId=target_id,
                    portNum=meshtastic.portnums_pb2.ROUTING_APP,
                    wantAck=True,
                    wantResponse=True
                )
                with self.lock:
                    self.pending_pings.add(target_id)
            else:
                print("📡 Broadcasting discovery ping...")
                self.interface.sendText("DISCOVERY_PING", channelIndex=0)
            
            return True
        except Exception as e:
            print(f"Error sending ping: {e}")
            return False
    
    def cascade_discovery(self):
        """Perform cascading node discovery"""
        print("\n" + "="*60)
        print("🔍 STARTING CASCADE DISCOVERY")
        print("="*60 + "\n")
        
        self.discovery_start_time = time.time()
        
        # Initial broadcast ping
        self.send_ping()
        time.sleep(5)
        
        # Request node database from local device
        print("Requesting node database...")
        if self.interface and self.interface.nodes:
            for node_id, node in self.interface.nodes.items():
                print(f"Known node: {node_id}")
        
        iteration = 1
        last_node_count = 0
        
        while not self.discovery_complete:
            elapsed = time.time() - self.discovery_start_time
            
            if elapsed > self.max_discovery_time:
                print("\n⏰ Max discovery time reached")
                self.discovery_complete = True
                break
            
            print(f"\n--- Iteration {iteration} (Elapsed: {elapsed:.1f}s) ---")
            
            with self.lock:
                current_count = len(self.discovered_nodes)
                new_nodes = current_count - last_node_count
                
                if new_nodes > 0:
                    print(f"✨ Discovered {new_nodes} new node(s)")
                    last_node_count = current_count
                
                # Send targeted pings to newly discovered nodes
                for node_id in list(self.discovered_nodes.keys()):
                    if node_id not in self.pending_pings:
                        self.send_ping(node_id)
                        time.sleep(2)
            
            # Send another broadcast
            self.send_ping()
            
            # Display current status
            self.display_discovery_status()
            
            # Check if discovery has stabilized
            if iteration > 3 and new_nodes == 0:
                print("\n✓ Discovery appears stable, waiting for final responses...")
                time.sleep(self.ping_interval)
                
                with self.lock:
                    if len(self.discovered_nodes) == last_node_count:
                        self.discovery_complete = True
                        break
            
            time.sleep(self.ping_interval)
            iteration += 1
        
        print("\n" + "="*60)
        print("✅ DISCOVERY COMPLETE")
        print("="*60)
        self.display_final_summary()
    
    def display_discovery_status(self):
        """Display current discovery status"""
        with self.lock:
            print(f"\n📊 Status: {len(self.discovered_nodes)} nodes discovered")
            print(f"⏳ Pending pings: {len(self.pending_pings)}")
    
    def display_final_summary(self):
        """Display final discovery summary"""
        print(f"\n📈 DISCOVERY SUMMARY:")
        print(f"   Total nodes found: {len(self.discovered_nodes)}")
        print(f"   Discovery time: {time.time() - self.discovery_start_time:.1f} seconds")
        
        print("\n📋 DISCOVERED NODES:")
        with self.lock:
            for node_id, data in self.discovered_nodes.items():
                info = self.node_metrics[node_id].get('info', {})
                name = info.get('longName', node_id)
                packets = data['packet_count']
                
                print(f"\n   🔹 {name} ({node_id})")
                print(f"      Packets: {packets}")
                
                metrics = self.node_metrics[node_id]
                if 'avg_snr' in metrics:
                    print(f"      SNR: {metrics['avg_snr']:.2f} dB")
                if 'avg_rssi' in metrics:
                    print(f"      RSSI: {metrics['avg_rssi']:.2f} dBm")
                if 'current_hop' in metrics:
                    print(f"      Hops away: {metrics['current_hop']}")
    
    def broadcast_custom_text(self, message):
        """Broadcast custom text to all nodes"""
        print(f"\n📢 Broadcasting custom message...")
        print(f"   Message: {message}")
        
        try:
            self.interface.sendText(message, channelIndex=0)
            print("✓ Text message sent")
            time.sleep(2)
            
            # Also send as direct messages to discovered nodes
            with self.lock:
                for node_id in self.discovered_nodes.keys():
                    try:
                        self.interface.sendText(
                            message,
                            destinationId=node_id,
                            wantAck=True
                        )
                        print(f"   ✓ Sent to {node_id}")
                        time.sleep(1)
                    except Exception as e:
                        print(f"   ✗ Failed to send to {node_id}: {e}")
            
            return True
        except Exception as e:
            print(f"✗ Broadcast failed: {e}")
            return False
    
    def prepare_audio_for_transmission(self, wav_file_path, chunk_size=200):
        """
        Prepare audio file for transmission over Meshtastic
        Note: Audio transmission is experimental and bandwidth-limited
        """
        try:
            print(f"\n🎵 Preparing audio file: {wav_file_path}")
            
            with wave.open(wav_file_path, 'rb') as wav_file:
                # Get audio parameters
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                print(f"   Channels: {channels}")
                print(f"   Sample width: {sample_width} bytes")
                print(f"   Frame rate: {framerate} Hz")
                print(f"   Duration: {n_frames/framerate:.2f} seconds")
                
                # Read audio data
                audio_data = wav_file.readframes(n_frames)
                
                # Encode to base64 for text transmission
                encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                
                # Split into chunks
                chunks = [encoded_audio[i:i+chunk_size] 
                         for i in range(0, len(encoded_audio), chunk_size)]
                
                print(f"   Total size: {len(audio_data)} bytes")
                print(f"   Encoded size: {len(encoded_audio)} bytes")
                print(f"   Chunks: {len(chunks)}")
                
                return {
                    'metadata': {
                        'channels': channels,
                        'sample_width': sample_width,
                        'framerate': framerate,
                        'duration': n_frames/framerate,
                        'total_chunks': len(chunks)
                    },
                    'chunks': chunks
                }
        except Exception as e:
            print(f"✗ Audio preparation failed: {e}")
            return None
    
    def broadcast_audio(self, audio_data):
        """
        Broadcast audio data to all nodes
        WARNING: This will take significant time due to bandwidth limitations
        """
        if not audio_data:
            print("✗ No audio data to broadcast")
            return False
        
        print(f"\n📻 Broadcasting audio transmission...")
        print(f"   ⚠️  This will take approximately {len(audio_data['chunks']) * 2} seconds")
        print(f"   Broadcasting {audio_data['metadata']['total_chunks']} chunks")
        
        try:
            # Send metadata first
            metadata_msg = f"AUDIO_START:{json.dumps(audio_data['metadata'])}"
            self.interface.sendText(metadata_msg, channelIndex=0)
            time.sleep(3)
            
            # Send chunks
            for i, chunk in enumerate(audio_data['chunks']):
                chunk_msg = f"AUDIO_CHUNK:{i}:{chunk}"
                self.interface.sendText(chunk_msg, channelIndex=0)
                print(f"   Sent chunk {i+1}/{len(audio_data['chunks'])}")
                time.sleep(2)  # Rate limiting
            
            # Send completion message
            self.interface.sendText("AUDIO_END", channelIndex=0)
            print("✓ Audio transmission complete")
            return True
            
        except Exception as e:
            print(f"✗ Audio broadcast failed: {e}")
            return False
    
    def save_metrics(self, filename='mesh_metrics.json'):
        """Save discovered metrics to JSON file"""
        print(f"\n💾 Saving metrics to {filename}...")
        
        with self.lock:
            data = {
                'discovery_time': time.time() - self.discovery_start_time,
                'total_nodes': len(self.discovered_nodes),
                'timestamp': datetime.now().isoformat(),
                'nodes': self.discovered_nodes,
                'metrics': dict(self.node_metrics)
            }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✓ Metrics saved successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to save metrics: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the Meshtastic device"""
        if self.interface:
            print("\nDisconnecting...")
            self.interface.close()
            print("✓ Disconnected")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("MESHTASTIC CASCADE DISCOVERY - LilyGo T-Watch S3")
    print("="*60)
    
    # Initialize discovery system
    discovery = MeshCascadeDiscovery(port='/dev/ttyACM0')
    
    # Connect to device
    if not discovery.connect():
        print("Failed to connect. Exiting.")
        return
    
    try:
        # Run cascade discovery
        discovery.cascade_discovery()
        
        # Save metrics
        discovery.save_metrics()
        
        # Broadcast custom text
        custom_message = """
🎯 MESH NETWORK DISCOVERY COMPLETE!

This message was sent after cascading through the entire mesh network.
All nodes have been discovered and catalogued.

Thank you for being part of this mesh network!
        """.strip()
        
        discovery.broadcast_custom_text(custom_message)
        
        # Optional: Audio broadcast (uncomment if you have an audio file)
        # audio_file = '/path/to/your/audio.wav'
        # audio_data = discovery.prepare_audio_for_transmission(audio_file)
        # if audio_data:
        #     response = input("\nBroadcast audio? This will take time (y/n): ")
        #     if response.lower() == 'y':
        #         discovery.broadcast_audio(audio_data)
        
        print("\n✅ All operations complete!")
        print("\nPress Ctrl+C to exit...")
        
        # Keep listening for responses
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutdown requested...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        discovery.disconnect()


if __name__ == "__main__":
    main()
