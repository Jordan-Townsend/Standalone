# Meshtastic Command Center - Complete Control Suite

A full-featured web-based control center for Meshtastic mesh networks with real-time map visualization, comprehensive node metrics, and complete communication capabilities. Perfect for emergency services, municipal deployments, and professional mesh network management.

![Command Center](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🌟 Features

### 🗺️ **Interactive Map Visualization**
- Real-time node positioning on OpenStreetMap
- Dynamic coverage area calculation
- Custom markers with node status indicators
- Click nodes for detailed popup information
- Automatic map centering and zoom

### 📊 **Comprehensive Metrics Dashboard**
- Live network statistics (nodes, messages, uptime)
- Per-node metrics (SNR, RSSI, hop count, battery)
- Signal quality visualization (color-coded)
- Historical data tracking
- Network health monitoring

### 💬 **Full Communication Suite**
- Broadcast messages to all nodes
- Direct messaging to specific nodes
- Emergency alert system
- Position updates
- Message history log with timestamps

### 🔍 **Intelligent Node Discovery**
- Automated cascade discovery
- Progressive network mapping
- Ping all nodes functionality
- Real-time node status updates
- Automatic position tracking

### ⚙️ **Advanced Configuration**
- Multi-region support (US, EU, CN, JP, ANZ)
- Custom device port selection
- Channel configuration
- Network preferences
- Export network data (JSON)

### 🎨 **Professional UI/UX**
- Cyberpunk-inspired dark theme
- Real-time updates without page refresh
- Responsive design for all devices
- Smooth animations and transitions
- Intuitive control layout

## 🚀 Installation

### Prerequisites

```bash
# Python 3.8 or higher
python3 --version

# Node.js (for optional development tools)
node --version
```

### 1. Clone/Download Files

```bash
# Create project directory
mkdir meshtastic-command-center
cd meshtastic-command-center

# Place all files in this directory
```

### 2. Install Python Dependencies

```bash
# Install required packages
pip install -r requirements_server.txt

# Or install individually
pip install meshtastic>=2.2.0 pypubsub>=4.0.3 websockets>=12.0
```

### 3. Connect Your Meshtastic Device

```bash
# Find your device port
ls /dev/tty*  # Look for /dev/ttyACM0 or /dev/ttyUSB0

# Check device permissions
ls -l /dev/ttyACM0

# Add yourself to dialout group if needed
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### 4. Configure the Server

Edit `meshtastic_server.py` if needed:

```python
server = MeshtasticServer(
    port='/dev/ttyACM0',      # Your device port
    ws_host='localhost',       # Server host
    ws_port=8765              # WebSocket port
)
```

## 🎯 Usage

### Starting the Server

```bash
# Start the backend server
python3 meshtastic_server.py
```

You should see:
```
Starting Meshtastic Command Center Server...
Connecting to Meshtastic device on /dev/ttyACM0...
✓ Connected to Meshtastic device
Starting WebSocket server on localhost:8765
✓ WebSocket server running
```

### Opening the Web Interface

#### Option 1: Simple HTTP Server (Recommended)

```bash
# In a new terminal, serve the HTML file
python3 -m http.server 8000

# Open in browser
# Visit: http://localhost:8000/meshtastic_command_center.html
```

#### Option 2: Direct File Access

```bash
# Open directly in browser
open meshtastic_command_center.html  # macOS
xdg-open meshtastic_command_center.html  # Linux
# Or drag the file into your browser
```

**Important**: Update the WebSocket connection in the HTML if needed:

```javascript
// Find this line in meshtastic_command_center.html
const ws = new WebSocket('ws://localhost:8765');
```

### Using the Interface

#### 1. **Connect to Device**
- Verify device port in "Device Config" panel
- Select your region
- Click "Connect Device"

#### 2. **Discover Network**
- Click "🔍 Start Discovery" button
- Watch as nodes appear on the map in real-time
- View metrics in the "Discovered Nodes" panel

#### 3. **Monitor Network**
- **Map**: See all nodes with their positions
- **Node List**: Click any node to focus on map
- **Message Log**: View all communications
- **Statistics**: Monitor network health

#### 4. **Communicate**
- **Broadcast**: Click "📢 Broadcast" to message all nodes
- **Ping All**: Click "📡 Ping All" to verify connectivity
- **Direct Messages**: Select target in broadcast modal

#### 5. **Export Data**
- Click "💾 Export Data" to download network info
- Includes all nodes, metrics, messages, and statistics
- Format: JSON

## 📡 API Reference

### WebSocket Messages

#### Client → Server

```javascript
// Start discovery
{
    "command": "start_discovery"
}

// Ping all nodes
{
    "command": "ping_all"
}

// Send broadcast message
{
    "command": "send_broadcast",
    "text": "Hello mesh network!",
    "message_type": "text"  // or "alert", "position"
}

// Connect to device
{
    "command": "connect_device",
    "port": "/dev/ttyACM0",
    "region": "US"
}

// Export data
{
    "command": "export_data"
}
```

#### Server → Client

```javascript
// Initial state
{
    "type": "init",
    "nodes": [...],
    "messages": [...],
    "stats": {...}
}

// Node update
{
    "type": "node_update",
    "node": {
        "id": "!a1b2c3d4",
        "name": "Base Station",
        "snr": 8.5,
        "rssi": -85,
        "hops": 0,
        "battery": 95,
        "position": {
            "latitude": 45.4981,
            "longitude": -122.4404
        }
    }
}

// New message
{
    "type": "message",
    "from": "Node Alpha",
    "from_id": "!e5f6g7h8",
    "text": "Message content",
    "timestamp": "2024-12-09T10:30:00"
}

// System message
{
    "type": "system_message",
    "from": "System",
    "text": "Discovery complete",
    "timestamp": "2024-12-09T10:30:00"
}

// Stats update
{
    "type": "stats_update",
    "stats": {
        "total_messages": 42,
        "total_nodes": 5,
        "start_time": "2024-12-09T10:00:00"
    }
}
```

## 🛠️ Advanced Configuration

### Custom Map Tiles

Edit the map initialization in `meshtastic_command_center.html`:

```javascript
// Change map style
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Or use satellite imagery
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Esri'
}).addTo(map);
```

### Adjusting Discovery Parameters

In `meshtastic_server.py`:

```python
async def start_discovery(self):
    # Adjust delays
    await asyncio.sleep(5)  # Wait after broadcast
    
    # Adjust ping intervals
    await asyncio.sleep(2)  # Between individual pings
```

### Custom Styling

Edit CSS variables in `meshtastic_command_center.html`:

```css
:root {
    --bg-dark: #0a0e17;
    --accent-cyan: #00d9ff;
    --accent-magenta: #ff006e;
    /* Customize colors here */
}
```

## 🔒 Security Considerations

### Network Security
- Use firewall rules to restrict WebSocket access
- Consider HTTPS/WSS for production deployments
- Implement authentication if exposing to internet

### Meshtastic Encryption
- All mesh messages use AES-256 encryption
- Channel keys are derived from channel name
- Use strong, unique channel names

### Best Practices
```bash
# Run on localhost only
ws_host='localhost'

# Use firewall to block external access
sudo ufw allow from 127.0.0.1 to any port 8765

# For LAN access, restrict to local network
sudo ufw allow from 192.168.1.0/24 to any port 8765
```

## 📱 T-Watch S3 Integration

### Connecting T-Watch S3

```python
# T-Watch S3 typically uses specific ports
port = '/dev/ttyACM0'  # or '/dev/ttyUSB0'

# Verify with
meshtastic --info --port /dev/ttyACM0
```

### T-Watch Specific Features

The T-Watch S3 includes:
- Built-in GPS (automatic position updates)
- Accelerometer (motion detection)
- Battery monitoring (shown in interface)
- Touch screen (can be programmed separately)

### Programming the Watch

```python
# The watch can run custom firmware
# Flash Meshtastic firmware to the watch
# Then it communicates via serial/Bluetooth

# Access via Bluetooth
from meshtastic.ble_interface import BLEInterface
interface = BLEInterface(address='XX:XX:XX:XX:XX:XX')
```

## 🚨 Emergency Services Use Cases

### 1. Disaster Response
- Deploy nodes at command posts
- Track first responder positions
- Broadcast emergency updates
- Monitor communication health

### 2. Search & Rescue
- Map team positions in real-time
- Coordinate search patterns
- Emergency beacon activation
- Dead zone identification

### 3. Municipal Backup Communications
- Backup system during outages
- Inter-department coordination
- Public safety announcements
- Infrastructure monitoring

### Example: Emergency Broadcast

```python
# Send high-priority alert
await server.send_broadcast(
    text="🚨 EMERGENCY: Evacuate to shelter Alpha",
    message_type="alert"
)

# This reaches all nodes simultaneously
# No infrastructure required
# Works during power/cell outages
```

## 📊 Performance Metrics

### Typical Performance
- **Node Discovery**: 1-5 minutes for 10-20 nodes
- **Message Latency**: 1-10 seconds depending on hops
- **Coverage**: 1-15km per node (line of sight)
- **Bandwidth**: ~1-5 kbps (text only)
- **Battery Life**: Days to weeks (solar recommended)

### Optimization Tips
- Elevate nodes for better coverage
- Use external antennas for range
- Minimize hop count (<4 hops ideal)
- Monitor SNR (>3 dB recommended)
- Use solar panels for permanent nodes

## 🔧 Troubleshooting

### Server Won't Start

```bash
# Check port permissions
ls -l /dev/ttyACM0
sudo chmod 666 /dev/ttyACM0

# Check if port is in use
lsof /dev/ttyACM0

# Try different port
python3 meshtastic_server.py --port /dev/ttyUSB0
```

### WebSocket Connection Failed

```javascript
// Check WebSocket URL in browser console
// Should match server settings

// Test WebSocket manually
const ws = new WebSocket('ws://localhost:8765');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
```

### No Nodes Discovered

1. **Check device connection**: `meshtastic --info`
2. **Verify region settings**: Nodes must be on same frequency
3. **Check range**: Nodes may be out of range
4. **Inspect logs**: Look for error messages in server output

### Map Not Loading

1. **Check internet connection**: Map tiles require internet
2. **Verify coordinates**: Default is Gresham, OR
3. **Browser console**: Check for JavaScript errors

## 🌐 Remote Access Setup

### Option 1: SSH Tunnel

```bash
# On remote server
python3 meshtastic_server.py

# On local machine
ssh -L 8765:localhost:8765 user@remote-server

# Access at localhost:8765
```

### Option 2: Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name mesh.example.com;

    location /ws {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

## 💡 Future Enhancements

Potential additions:
- [ ] Voice message recording/playback
- [ ] File transfer over mesh
- [ ] Automated node health alerts
- [ ] Historical data analysis
- [ ] Multi-device control
- [ ] Mobile app companion
- [ ] Integration with ATAK/Winlink
- [ ] Mesh routing visualization

## 📄 License

MIT License - feel free to use and modify for your needs.

## 🤝 Contributing

Contributions welcome! This is especially valuable for:
- Emergency services organizations
- Disaster preparedness groups
- Mesh networking enthusiasts
- Municipal technology departments

## 📞 Support

For issues and questions:
- Meshtastic Discord: https://discord.gg/meshtastic
- Meshtastic Docs: https://meshtastic.org/docs/

---

**Built for professionals who need reliable, off-grid communication when it matters most.**

*"When the infrastructure fails, the mesh network stands."*
