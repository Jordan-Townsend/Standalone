# 🚀 Quick Start Guide - Meshtastic Command Center

Get up and running in 10 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check if you have pip
pip3 --version

# Check for Meshtastic device
ls /dev/tty*  # Look for /dev/ttyACM0 or /dev/ttyUSB0
```

## Installation (5 minutes)

### Step 1: Install Dependencies

```bash
# Install Python packages
pip3 install meshtastic pypubsub websockets

# If that fails, try:
pip3 install --user meshtastic pypubsub websockets
```

### Step 2: Test Device Connection

```bash
# Test that Meshtastic CLI works
meshtastic --info

# If you get an error about permissions:
sudo usermod -a -G dialout $USER
# Then log out and back in
```

## Running the System (2 minutes)

### Step 1: Start Backend Server

```bash
# Open a terminal and run:
python3 meshtastic_server.py

# You should see:
# ✓ Connected to Meshtastic device
# ✓ WebSocket server running
```

**Leave this terminal open!**

### Step 2: Start Web Server

```bash
# Open a NEW terminal and run:
python3 -m http.server 8000

# You should see:
# Serving HTTP on :: port 8000
```

**Leave this terminal open too!**

### Step 3: Open Browser

1. Open your web browser
2. Go to: `http://localhost:8000/meshtastic_command_center.html`
3. You should see the Command Center interface!

## First Use (3 minutes)

### 1. Verify Connection
- Look at the top right corner
- Should show "Connected" with a green dot
- Should show "Nodes: 0" initially

### 2. Start Discovery
- Click the **"🔍 Start Discovery"** button
- Watch the message log for updates
- Nodes will appear on the map as they're discovered

### 3. Explore the Interface
- **Map**: Shows node positions (if they have GPS)
- **Node List**: Shows all discovered nodes with metrics
- **Message Log**: Shows all communications
- **Statistics**: Shows network health

### 4. Try Broadcasting
- Click **"📢 Broadcast"** button
- Type a message
- Click "Send"
- All nodes will receive it!

## Demo Mode

If you don't have a Meshtastic device connected:

The system automatically runs in **demo mode** with simulated nodes!
- Simulated nodes will appear during discovery
- You can test all features
- Great for demonstrations

## Troubleshooting

### "Can't connect to device"
```bash
# Check if device is connected
meshtastic --info

# Check permissions
ls -l /dev/ttyACM0
sudo chmod 666 /dev/ttyACM0
```

### "WebSocket connection failed"
- Make sure the Python server is running
- Check for error messages in the terminal
- Try refreshing the browser

### "No nodes found"
- Nodes must be on the same frequency/region
- Check that nodes are powered on
- Try increasing discovery time
- Demo mode will show simulated nodes

### "Map not loading"
- Requires internet connection for map tiles
- Check browser console for errors
- Try refreshing the page

## Next Steps

1. **Read the Full Docs**: `COMMAND_CENTER_README.md`
2. **Configure Your Region**: In the Device Config panel
3. **Add More Nodes**: Deploy additional Meshtastic devices
4. **Explore Features**: Try broadcast, ping, export data
5. **Customize**: Edit colors, map style, etc.

## Common Commands

```bash
# Stop the servers
# Press Ctrl+C in each terminal

# Restart backend with different port
python3 meshtastic_server.py --port /dev/ttyUSB0

# Run on different WebSocket port
# Edit meshtastic_server.py, change ws_port=8765

# View Meshtastic device info
meshtastic --info

# List all Meshtastic nodes
meshtastic --nodes

# Send a test message
meshtastic --sendtext "Hello from CLI"
```

## File Structure

```
meshtastic-command-center/
├── meshtastic_command_center.html  # Frontend interface
├── meshtastic_server.py            # Backend WebSocket server
├── meshtastic_cascade_discovery.py # CLI discovery tool
├── audio_generator.py              # Voice message creator
├── requirements_server.txt         # Python dependencies
├── COMMAND_CENTER_README.md        # Full documentation
├── MARKET_ANALYSIS.md              # Business value analysis
└── QUICKSTART.md                   # This file
```

## Tips & Tricks

### Run on Startup (Linux/macOS)

Create a startup script:

```bash
#!/bin/bash
# start_meshtastic.sh

cd /path/to/meshtastic-command-center
python3 meshtastic_server.py &
python3 -m http.server 8000 &

echo "Meshtastic Command Center started!"
echo "Open: http://localhost:8000/meshtastic_command_center.html"
```

Make it executable:
```bash
chmod +x start_meshtastic.sh
./start_meshtastic.sh
```

### Access from Other Devices (Same Network)

1. Find your IP address:
```bash
# Linux/macOS
ifconfig | grep "inet "

# Look for something like 192.168.1.100
```

2. On other devices, visit:
```
http://192.168.1.100:8000/meshtastic_command_center.html
```

### Use with T-Watch S3

The LilyGo T-Watch S3 works just like any other Meshtastic device:

1. Flash Meshtastic firmware to the watch
2. Connect via USB or Bluetooth
3. It will appear in the node list automatically
4. GPS coordinates from the watch will show on the map!

## Support & Resources

- **Meshtastic Docs**: https://meshtastic.org/docs/
- **Meshtastic Discord**: https://discord.gg/meshtastic
- **Hardware Vendors**:
  - RAKwireless: https://store.rakwireless.com/collections/meshtastic
  - Heltec: https://heltec.org/
  - LilyGo: https://www.lilygo.cc/

## What to Try Next

1. **Add More Nodes**: Deploy 2-3 more Meshtastic devices
2. **Test Range**: See how far apart nodes can be
3. **Create Channels**: Set up different channels for different groups
4. **Export Data**: Try the export function to save network data
5. **Audio Messages**: Use audio_generator.py to create voice broadcasts

---

**You're now ready to use Meshtastic Command Center!**

For questions, check the full documentation or the Meshtastic community forums.

🎯 **Pro Tip**: Start with 3 nodes to create your first mesh network. Place them at different heights (roof, ground floor, basement) to test coverage.
