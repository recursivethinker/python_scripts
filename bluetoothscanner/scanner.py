import asyncio
from bleak import BleakScanner

async def scan_detailed():
    print(f"{'Name':<30} | {'Address':<20} | {'Manufacturer/Services'}")
    print("-" * 80)
    
    # We use a detection callback to capture data as it arrives
    devices = await BleakScanner.discover(return_adv=True)
    
    for d, adv in devices.values():
        name = d.name if d.name else "Unknown Device"
        address = d.address
        
        # Extract Manufacturer Data (Company IDs)
        # Format: {CompanyID: DataBytes}
        mfr_data = list(adv.manufacturer_data.keys()) if adv.manufacturer_data else "None"
        
        # Extract Service UUIDs (Device functions)
        services = adv.service_uuids if adv.service_uuids else []
        
        print(f"{name[:30]:<30} | {address:<20} | Mfr IDs: {mfr_data} | Services: {services}")

if __name__ == "__main__":
    asyncio.run(scan_detailed())
