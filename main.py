import usb.core
import usb.util
import time
import os
import smtplib
from plyer import notification
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define authorized USB device IDs (Vendor ID, Product ID, Serial Number)
authorized_devices = [
    (0x7825, 0xa2a4, "235678C218CA"),  # Example Vendor ID, Product ID, and Serial Number for Device 1
    (0x1234, 0x5678, "ABC123XYZ"),  # Example Vendor ID, Product ID, and Serial Number for Device 2
]

# Email configuration
EMAIL_ADDRESS = 'vickhami@gmail.com'  # Replace with your email
EMAIL_PASSWORD = 'nvbltvekfqlupokv'  # Replace with your app-specific email password
TO_EMAIL_ADDRESS = 'splenndority@gmail.com'  # Replace with recipient's email

# Function to send email notification
def send_email_notification(unauthorized_devices):
    subject = "Unauthorized USB Device Detected"
    body = "The following unauthorized USB devices were detected:\n"
    for device in unauthorized_devices:
        body += f"Vendor ID: {device[0]}, Product ID: {device[1]}, Serial: {device[2]}\n"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL_ADDRESS
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # Using SSL for secure connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email notification sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to send desktop notification
def send_desktop_notification(unauthorized_devices):
    notification_title = "Unauthorized USB Device Detected"
    notification_message = "Check your USB devices!"

    notification.notify(
        title=notification_title,
        message=notification_message,
        app_name='USB Monitor',
        timeout=10  # Notification duration in seconds
    )
    print("Desktop notification sent.")

# Function to block/unmount unauthorized USB devices
def block_usb_device(device):
    # Attempt to unmount the device using diskutil
    try:
        os.system(f'sudo diskutil unmount /dev/disk{device}')  # Adjust based on actual device identifier
        print(f"Device disk{device} unmounted.")
    except Exception as e:
        print(f"Error unmounting device: {e}")

# Function to get the currently connected USB devices
def get_connected_usb_devices():
    devices = []
    for dev in usb.core.find(find_all=True):
        try:
            serial_number = usb.util.get_string(dev, dev.iSerialNumber)  # Retrieve serial number
        except usb.core.USBError:
            serial_number = None  # Handle cases where serial number is not available
        print(f"Detected Device - Vendor ID: {dev.idVendor}, Product ID: {dev.idProduct}, Serial: {serial_number}")
        devices.append((dev.idVendor, dev.idProduct, serial_number))
    return devices

# Function to monitor USB devices and alert for unauthorized ones
def monitor_usb_devices():
    try:
        while True:
            connected_devices = get_connected_usb_devices()
            unauthorized_devices = [dev for dev in connected_devices if dev not in authorized_devices]

            if unauthorized_devices:
                print("Unauthorized USB Devices Detected:")
                for device in unauthorized_devices:
                    print(f"Vendor ID: {device[0]}, Product ID: {device[1]}, Serial: {device[2]}")
                send_desktop_notification(unauthorized_devices)  # Send desktop notification
                send_email_notification(unauthorized_devices)  # Send email notification

                # Attempt to unmount the first unauthorized device (adjust based on actual identifier format)
                block_usb_device("2s1")  # Adjust device identifier as needed
            else:
                print("All connected USB devices are authorized.")

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user. Exiting...")

# Start monitoring USB devices
monitor_usb_devices()
