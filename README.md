
# E-VPN 

This script automates the setup of an OpenVPN configuration using the fastest available VPN gateway from [Riseup's API](https://api.black.riseup.net/3/config/eip-service.json). 
## Features
- Fetches VPN client certificates from Riseup's API
- Retrieves VPN gateway configurations from Riseup's API
- Measures latency to each VPN gateway
- Configures OpenVPN to use the fastest available gateway

Special thanks to the [Riseup/LEAP](https://0xacab.org/leap) team for providing the VPN client certificates and gateway configurations through their API.

