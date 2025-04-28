# import os
# import subprocess

# def send_notification(title, message):
#     # subprocess.run([
#     #     'osascript', 
#     #     '-e', 
#     #     f'display notification "{title}" with title "{message}"'
#     # ])
#     subprocess.run(['terminal-notifier', '-title', title, '-message', message])
#     print(f"Sending notification: {title} - {message}")


# if __name__ == "__main__":
#     send_notification("Test Notification", "This is a test notification to check if notifications are working.")







import Foundation
import objc
from Foundation import NSUserNotification, NSUserNotificationCenter

def send_notification(title, message): 

    notification = NSUserNotification.alloc().init()
    notification.setTitle_(title)
    notification.setInformativeText_(message)
    
    # Get the default notification center
    notification_center = NSUserNotificationCenter.defaultUserNotificationCenter()
    
    # Check if the notification center is valid
    if notification_center is not None:
        notification_center.deliverNotification_(notification)
    else:
        print("Notification center is not available.")

if __name__ == "__main__":
    send_notification("Test Notification", "This is a test notification to check if notifications are working.")

