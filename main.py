import subprocess
import threading
import time
import os

PATH = os.path.dirname(__file__)
GASTER_STATE = False

def restart_winmgmt():
    try:
        # Stop the WMI service
        print("Stopping WMI service...")
        subprocess.run(["net", "stop", "winmgmt"], check=True, shell=True, timeout=30)
        print("Stopped WMI service.")

        # Start the WMI service
        print("Starting WMI service...")
        subprocess.run(["net", "start", "winmgmt"], check=True, shell=True, timeout=30)
        print("Started WMI service.")

    except subprocess.TimeoutExpired:
        print("Timeout expired while restarting WMI service.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while restarting WMI: {e}")

restart_winmgmt()

from wmi import WMI

def driverfix():
    print("[*] Fixing iDevice driver")
    try:
        subprocess.run(f'pnputil /add-driver "{PATH}\\driver\\AppleUsb.inf" /install', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running driverfix: {e}")

def ideviceid():
    for device in WMI().Win32_PnPEntity(ConfigManagerErrorCode=0):
        if 'Apple' in str(device.Caption):
            DeviceHardwareID  = device.HardwareID[-1].split("&")
            DeviceVID = DeviceHardwareID[0].split("_")[-1]
            DevicePID = DeviceHardwareID[1].split("_")[-1]

            return DeviceVID, DevicePID

    return 0, 0

def idevicegetstate(): # -1=none 0=normal, 1=recovery, 2=dfu, 3=pwndfu
    DeviceVID, DevicePID = ideviceid()
    DeviceVID = int(f"0x{DeviceVID}", 16)
    DevicePID = int(f"0x{DevicePID}", 16)

    if DevicePID == 0x12a8: # Normal Mode
        # print("iDevice in Normal Mode")
        return 0
    elif DevicePID == 0x1281: # Recovery Mode
        # print("iDevice in Recovery Mode")
        return 1
    elif DevicePID == 0x1227: # DFU Mode
        # print("iDevice in DFU Mode")
        return 2
    
    # print("iDevice not Connected")
    return -1

def device_driver_which(): # return True if driver is libusbk, False if driver is Apple, Inc.
    os.system("powershell -Command Restart-Service -Force -Name winmgmt")

    c = WMI()
    for driver in c.Win32_PnPSignedDriver():
        if "Apple" in str(driver.DeviceName):
            if "Apple, Inc." == str(driver.DriverProviderName):
                return 1
            if "libusbK" == str(driver.DriverProviderName):
                return 2

    return 0

def idevice_id():
    output = ""

    try:
        output = subprocess.check_output([f"{PATH}\\tools\\idevice_id\\idevice_id.exe", "-l"], shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running idevice_id: {e}")

    return output.strip()

def ideviceenterrecovery():
    output = ""

    try:
        output = subprocess.check_output([f"{PATH}\\tools\\ideviceenterrecovery\\ideviceenterrecovery.exe", idevice_id()], shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running ideviceenterrecovery: {e}")

    return output

def gotodfu():
    try:
        subprocess.check_output([f"{PATH}\\tools\\irecovery\\irecovery.exe", "-n"], shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running irecovery: {e}")

def idevicestate():
        output = ""

        try:
            output = subprocess.check_output([f"{PATH}\\tools\\irecovery\\irecovery.exe", "-q"], shell=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running irecovery: {e}")
        
        # print(output)
        if "GASTER" in output:
            return 3
        if "Recovery" in output:
            return 1
        if "DFU" in output:
            return 2

        return 0

def libusbk(vid, pid):
    try:
        os.system(f'{PATH}\\tools\\wdi-simple\\wdi-simple.exe --name "Apple Mobile Device (DFU Mode)" --vid 0x{str(vid)} --pid 0x{str(pid)} --type 2')
    except:
        ...

def irecovery_product():
    output = ""

    try:
        output = subprocess.check_output([f"{PATH}\\tools\\irecovery\\irecovery.exe", "-q"], shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running irecovery: {e}")

    for i in output.split("\n"):
        if "PRODUCT" in i:
            return i.replace("PRODUCT: ", "")

def irecovery_iBEC():
    try:
        os.system(f'{PATH}\\tools\\irecovery\\irecovery.exe -f "{PATH}\\tools\\irecovery\\boot\\{irecovery_product()}\\iBEC.img4"')
    except:
        print("[!] Error with running irecovery")

def gaster():
    global GASTER_STATE

    try:
        os.system(f"{PATH}\\tools\\gaster\\gaster.exe pwn")
    except:
        ...

    GASTER_STATE = True

def main():
    global GASTER_STATE

    gaster_thread = threading.Thread(target=gaster)

    if idevicegetstate() == 0: # if iDevice in Normal Mode
        print("[*] iDevice in Normal Mode, trying to put into Recovery Mode")
        if device_driver_which() != 1:
            driverfix()
        ideviceenterrecovery() # go to Recovery Mode

    while idevicegetstate() == -1 or idevicegetstate() == 0:
        time.sleep(0.5)

    if idevicegetstate() == 1:
        while_true = True
        while while_true: # if iDevice in Recovery Mode go to DFU Mode
            print("[*] iDevice in Recovery Mode, trying to put into DFU Mode")
            if device_driver_which() != 1:
                driverfix()

            input("Press Enter when you're ready to enter DFU mode...")

            first_time = 3
            second_time = 10

            print(f"[!] Press and hold Home (Volume Down) + Power button ({first_time})")
            time_start = time.time()

            time_old = int(time.time() - time_start)
            gotodfu_state = True

            while first_time - (time.time() - time_start) > -1:
                time_new = int(time.time() - time_start)
                if time_new != time_old:
                    time_old = time_new
                    if first_time - time_old != -1:
                        print(f"[!] Press and hold Home (Volume Down) + Power button ({first_time - time_old})")

                    if first_time - time_old == 2 and gotodfu_state:
                        gotodfu_state = False
                        gotodfu() # run irecovery -n

            print(f"[!] Release the Power button but keep holding the Home button (Volume Down) ({second_time})")
            time_start = time.time()
            time_old = int(time.time() - time_start)
            while time.time() - time_start < second_time + 0.1:
                time_new = int(time.time() - time_start)
                if time_new != time_old:
                    time_old = time_new
                    print(f"[!] Release the Power button but keep holding the Home button (Volume Down) ({second_time - time_old})")

                if idevicegetstate() == 2:
                    break

            while idevicegetstate() == -1:
                time.sleep(0.5)
            while_true = idevicegetstate() == 1

            if while_true:
                print("[!] Error with going to DFU. Try again...")

    if idevicegetstate() == 2:# and idevicestate() != 3: # if iDevice in DFU Mode and not on PWNDFU
        iDeviceVID, iDevicePID = ideviceid()

        print("[*] Trying to put iDevice to PWNDFU Mode")

        if device_driver_which() != 2:
            print("[*] Changing iDevice driver to libusbK")
            libusbk(iDeviceVID, iDevicePID)

        # gaster_thread.daemon = True
        gaster_thread.start()

        if idevicegetstate() == 1:
            print("[!] Error with going to PWNDFU. Try again...")
            os._exit(0)

        libusbk_fix = True
        while not GASTER_STATE:
            while idevicegetstate() == -1:
                time.sleep(0.5)

            if idevicegetstate() == 1:
                print("[!] Error with going to PWNDFU. Try again...")
                os._exit(0)

            if idevicegetstate() == 2 and libusbk_fix:
                if device_driver_which() != 2:
                    if (not GASTER_STATE):
                        libusbk_fix = False
                        print("[*] Changing iDevice driver to libusbK")
                        libusbk(iDeviceVID, iDevicePID)

        gaster_thread.join()

        while idevicegetstate() == -1:
            time.sleep(0.5)

    if idevicegetstate() == 2:# if iDevice in DFU Mode and not on PWNDFU
        if device_driver_which() != 1:
            driverfix()
        if idevicestate() == 3: # if iDevice
            print("[*] iDevice in PWNDFU Mode, trying to boot iDevice")
            irecovery_iBEC()
            irecovery_iBEC()

if __name__ == "__main__":
    os.system("powershell -Command Restart-Service -Force -Name winmgmt")

    main()
