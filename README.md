# Meshtastic Standalone Command Center
A fully offline, single-file web interface for managing Meshtastic mesh networks.

---

## Overview

The Meshtastic Standalone Command Center is a zero-dependency, browser-based management interface for Meshtastic mesh networks. It runs entirely from a single HTML file, requires no backend server, no installation, and no internet connection.

This project is built for reliability in field conditions, emergency scenarios, research environments, and any situation where a universal control interface is needed across a wide range of hardware.

---

## Key Features

### Offline and Self-Contained
- Runs from a single 51KB HTML file  
- 100% offline capability (PWA support)  
- No framework dependencies and no cloud services  

### Universal Connectivity
Supports native browser APIs:
- Web Bluetooth  
- Web Serial  
- WiFi / HTTP connections  
- Auto-detection of supported transports  

### Comprehensive Mesh Management
- Real-time map of all nodes  
- Mesh metrics: RSSI, SNR, hop count, routing details  
- Broadcast and message console  
- Node configuration and diagnostics  
- Event logs and data export  

### Cross-Platform Compatibility
Works on:
- Laptops (Windows, Linux, macOS)  
- Tablets and smartphones  
- Smartwatches with WebView + BLE  
- Any modern browser supporting Web Bluetooth / Web Serial  

No installation required — open the file and connect.

---

## Why This Exists

Meshtastic is a powerful platform, but existing interfaces are tied to mobile apps, desktop installations, backend services, or cloud connectivity. In off-grid or emergency situations, these dependencies create unnecessary friction.

This project delivers:

- A reliable offline interface  
- A portable tool that works anywhere  
- A universal command system for field deployment  
- A professional dashboard for teams, researchers, and builders  

Its goal is to make resilient communication truly accessible.

---

## Getting Started

### 1. Download
Download the standalone HTML file:

```
[Insert your download link here]
```

### 2. Open in Your Browser
Open the file with:
- Chrome  
- Edge  
- Chromium-based browsers  
- Android Chrome  
- Safari (partial Bluetooth support)  

### 3. Connect to Your Device
Choose your preferred connection method:
- Bluetooth  
- USB Serial  
- WiFi/HTTP  

No drivers or installation required.

---

## Supported Hardware

Tested and community-validated hardware includes:

- LilyGo T-Beam variants  
- Heltec boards  
- RAK WisBlock modules  
- LilyGo T-Watch S3  
- Custom Meshtastic devices  

If your hardware works, please open an issue to add it to the list.

---

## Roadmap

Planned improvements:
- Node provisioning tools  
- Fleet-level monitoring  
- Multi-mesh dashboards  
- Offline map tile caching  
- Enhanced routing visualization  
- Optional cloud sync (opt-in only)  
- Native mobile wrappers  

Feature suggestions are welcome.

---

## Contributing

Ways to contribute:
- Hardware testing  
- Bug reports  
- Feature suggestions  
- Pull requests  
- Documentation improvements  

Open an issue with as much detail as possible.

---

## Development Philosophy

This project is intentionally simple:
- No frameworks  
- No build process  
- No backend infrastructure  
- No telemetry  
- No analytics  

Everything runs inside the standalone HTML file for maximum transparency and reliability.

---

## Security Considerations

- No data leaves your local device  
- No cloud logging or analytics  
- All communications stay within the browser and your Meshtastic hardware  
- Users maintain complete control of their mesh and configuration  

---

## License

Choose the license appropriate for your repository:

- Apache 2.0  
- MIT License  
- MPL 2.0  

Ask if you’d like these generated for you.

---

## Support and Contact

If you are part of an emergency communications group, research lab, hardware vendor, or organization interested in professional integrations or deployment support, feel free to reach out.

General inquiries can be submitted through GitHub Issues.

---

## Acknowledgments

Thanks to the Meshtastic development community for building the foundation that enables projects like this. This tool exists because of their continued work and dedication.

This was initally ai generated. Human maintained. 


I'm currently awaiting my first meshtastic node to arrive. A Lilygo S3 watch. If you have any spare hardware that needs to be tested on the network let me know. Jordan@townsendsdesigns.com
