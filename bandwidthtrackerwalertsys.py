
import sys 
import random
import time
import smtplib
import pyqtgraph as pg
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PyQt5 import QtWidgets, QtCore
from threading import Thread
import psutil
    
isemailsent = False 

class BandwidthTracker(QtWidgets.QWidget): 

    
    def __init__(self, parent=None): # Initializing the Graph class
        super(BandwidthTracker, self).__init__(parent)  # Calling the parent class constructor
        self.init_ui()  # Initializing the user interface
        self.running = False # Set the program to not running   

    def init_ui(self):
        
        self.start_bytes =  0 
        self.total_usage = 0
        self.megabyte_received = 0
        self.megabyte_sent = 0
        self.megabyte_total = 0
        
        self.layout = QtWidgets.QVBoxLayout(self) # Create a vertical layout
        self.setWindowTitle("Bandwidth Tracker") # Set the window title

        # Setup UI components
        self.setup_ui_components() 

        self.graph_widget = pg.GraphicsWindow() # Creating a pyqtgraph widget
        self.layout.addWidget(self.graph_widget) # Add the pyqtgraph to the program interface
        self.layout.addWidget(self.start_button) # Add the start button to the program interface
        self.layout.addWidget(self.my_label) # Add the status labelto the program interface

        self.graph_ids = ['received bytes', 'send bytes', 'total bytes'] # Define the graph ids
        self.curves = [] # Store the curves to show on the graph
        self.data = {id: [] for id in self.graph_ids} # Store the data for each graph id

        for id in self.graph_ids: # Create a plot for each graph id
            plot = self.graph_widget.addPlot(title=id) # Add a plot to the pyqtgraph widget
            plot.setXRange(0, 100) # Set the x-axis range
            curve = plot.plot(pen=pg.mkPen(color=random.choice(["#803723", "#1ff2ed", "#00fa5c"]))) # Add a curve to the plot
            self.curves.append(curve) # Store the curve
            self.graph_widget.nextRow() # Move to the next row

        self.timer = QtCore.QTimer() # Create a timer
        self.timer.timeout.connect(self.update_graph) # Connect the timer to the update_graph function

    def setup_ui_components(self):
        
        self.start_button = QtWidgets.QPushButton("Start") # Creating a start button
        self.start_button.clicked.connect(self.start_reading) # Connecting the start button to the start_reading function
        self.start_button.setFixedSize(100, 50) # Settng the size of the start button
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 20px; font-weight: bold; border-radius: 10px; border: 2px solid #4CAF50;") # Setting the style of the start button

        # Status label added 
        self.my_label = QtWidgets.QLabel(self.yazdir()) # Creating a status label

        # Checkboxes added
        self.email_checkbox = QtWidgets.QCheckBox("Send e-mail when usage exceeds.") # Creating a checkbox for email
        self.total_usage_checkbox = QtWidgets.QCheckBox("Alert with total usage") # Creating other checkbox for alert
        self.threshold_alert_checkbox = QtWidgets.QCheckBox("Alert with current usage threshold") # Creating last checkbox for alert
        self.layout.addWidget(self.email_checkbox) # Adding the checkbox to the layout
        self.layout.addWidget(self.total_usage_checkbox) 
        self.layout.addWidget(self.threshold_alert_checkbox) 

        # Text Entries added
        self.email_entry = QtWidgets.QLineEdit() # Creating a text entry
        self.email_entry.setPlaceholderText("E-mail address") # Setting the placeholder text
        self.threshold_entry = QtWidgets.QLineEdit() # Creating a text entry
        
        self.layout.addWidget(self.email_entry) # Adding the text entry to the layout
        self.layout.addWidget(self.threshold_entry) # Adding the text entry to the layout

        # Connecting the checkboxes
        self.total_usage_checkbox.stateChanged.connect(self.check_total_usage) # Connecting the checkbox to the check_total_usage function
        self.threshold_alert_checkbox.stateChanged.connect(self.check_threshold_alert) # Connecting the checkbox to the check_threshold_alert function

    def check_total_usage(self, state): # Checking if the total usage checkbox is checked
        if state == QtCore.Qt.Checked:
            self.threshold_alert_checkbox.setChecked(False)
            self.threshold_entry.setPlaceholderText("Please Enter the Total Usage Limit in MB")

    def check_threshold_alert(self, state): # Checking if the threshold alert checkbox is checked
        if state == QtCore.Qt.Checked:
            self.total_usage_checkbox.setChecked(False)
            self.threshold_entry.setPlaceholderText("Please Enter Usage Threshold in MB")
    
    def yazdir(self): # Print the current internet usage
        return(f"Received: {self.megabyte_received:.4f} MB/s received, Sent: {self.megabyte_sent:.4f} MB/s sent, Total: {self.megabyte_total:.4f} MB/s total: {self.total_usage:.4f} MB of usage")

    
    def send_email(self): # Send an email if the bandwidth usage exceeds the threshold
        global isemailsent 
       
        if isemailsent == False: # Check if the email has already been sent     
            
            sender_email = "bandwidth_alert_system@outlook.com" # sender email
            sender_password = "Dummy4901" #sender password
            receiver_email = self.email_entry.text() #receiver email, take from the user
            subject = "Alert! Bandwidth Usage Exceeded!" # email subject 
            body = "Your bandwidth usage has exceeded the threshold! Please check your usage." # email body 

            message = MIMEMultipart() # Create a MIME message 
            #MIMEText is a class to translate e-mail messages into MIME format in python programming language. 
            # e-mail messages by expanding e-mail standards
            # It allows it to contain text, HTML content, images, audio files and other 
            # multimedia files.
            

            message['From'] = sender_email # Set the sender email 
            message['To'] = receiver_email # Set the receiver email
            message['Subject'] = subject # Set the email subject
            message.attach(MIMEText(body, 'plain')) # Attach the email body

            smtp_server = "smtp.office365.com" # Set the SMTP server
            #Bu string, Microsoft'un Office 365 hizmeti için SMTP sunucusunun adresini belirtir.
            smtp_port = 587 # Set the SMTP port
            
            if self.email_checkbox.isChecked(): # Check if the email checkbox is checked
                if self.threshold_alert_checkbox.isChecked(): # Check if the threshold alert checkbox is checked
                
                    try: # Try to send the email
                        if self.threshold_entry.text() != "": # Check if the threshold entry is not empty
                            if self.megabyte_total > float(self.threshold_entry.text()): # Check if the total usage exceeds the threshold
                                print("Sending email...") 
                                server = smtplib.SMTP(smtp_server, smtp_port) # Create an SMTP server
                                server.starttls() # Start the SMTP server
                                server.login(sender_email, sender_password) # Login to the SMTP server
                                server.sendmail(sender_email, receiver_email, message.as_string()) # Send the email

                                server.quit() # Quit the SMTP server
                                isemailsent = True # Set the email sent to True
                                print("Email sent successfully!")  
                        

                    except Exception as e: # Handle exceptions
                        print("Failed to send email. Error:", str(e))

           
                elif self.total_usage_checkbox.isChecked(): # Check if the total usage checkbox is checked
                
                    try:
                        if self.threshold_entry.text() != "": # Check if the threshold entry is not empty
                            if self.total_usage > float(self.threshold_entry.text()): # Check if the total usage exceeds the threshold
                                print("Sending email...") 
                                server = smtplib.SMTP(smtp_server, smtp_port) # Create an SMTP server
                                server.starttls() # Start the SMTP server
                                server.login(sender_email, sender_password) # Login to the SMTP server
                                server.sendmail(sender_email, receiver_email, message.as_string()) # Send the email
                                server.quit() # Quit the SMTP server
                                isemailsent = True # Set the email sent to True
                                print("Email sent successfully!")
                        

                    except Exception as e:
                        print("Failed to send email. Error:", str(e))

      

    def start_reading(self):
        if not self.running: # Check if the program is not running
            self.running = True # Set the program to running
            self.thread = Thread(target=self.read_data) # Create a thread for reading data 
            self.thread.daemon = True # Set the thread to daemon
            # A daemon thread is a thread that runs in the background without blocking the execution of the main program.
            self.thread.start() # Starting the thread 
            self.timer.start(30) # Starting the timer

    def read_data(self):
        
        global last_received, last_sent, total # To use outside of the function

        last_received = last_sent = total = 0 # Initializes the variables
        current_stats = psutil.net_io_counters() # Gets the current network statistics
        new_received = current_stats.bytes_recv - last_received # Calculates the new received bytes
        new_sent = current_stats.bytes_sent - last_sent # Calculate the new sent bytes
        new_total = new_received + new_sent # Calculate the new total bytes
            
        last_received = current_stats.bytes_recv # Updates the last received bytes
        last_sent = current_stats.bytes_sent # Updates the last sent bytes
        total = new_received + new_sent # Updates the total bytes

        current_stats = psutil.net_io_counters() # Gets the current network statistics
        self.start_bytes = current_stats.bytes_recv + current_stats.bytes_sent # Gets the start bytes
        self.total_usage = self.start_bytes 
        self.megabyte_received = current_stats.bytes_recv / 1024 / 1024 # Calculates the received megabytes
        self.megabyte_sent = current_stats.bytes_sent / 1024 / 1024 # Calculates the sent megabytes
        self.megabyte_total = self.megabyte_received + self.megabyte_sent # Calculates the total megabytes


        while self.running:
            current_stats = psutil.net_io_counters() # Gets the current network statistics
            new_received = current_stats.bytes_recv - last_received # Calculates the new received bytes
            new_sent = current_stats.bytes_sent - last_sent # Calculates the new sent bytes
            new_total = new_received + new_sent # Calculates the new total bytes

            self.total_usage = (current_stats.bytes_recv+ current_stats.bytes_sent - self.start_bytes) / 1024 / 1024 # Calculates the total usage 
            
            self.data['received bytes'].append(new_received) # Append the new received bytes uappend can make available to select incoming data end-to-end.
            self.data['send bytes'].append(new_sent) # Append the new sent bytes
            self.data['total bytes'].append(new_total) # Append the new total bytes 
            
            last_received = current_stats.bytes_recv # Update the last received bytes
            last_sent = current_stats.bytes_sent # Update the last sent bytes
            total = new_received + new_sent # Update the total bytes

            self.megabyte_received = new_received / 1024 / 1024 #byte to megabyte
            self.megabyte_sent = new_sent / 1024 / 1024 #byte to megabyte
            self.megabyte_total = new_total / 1024 / 1024 #byte to megabyte
            
            time.sleep(0.05)  # Adjust timing according to needs
            self.send_email()

    def update_graph(self):
        
        for curve, id in zip(self.curves, self.graph_ids): 
            if len(self.data[id]) > 100: # Keep only the last 100 points
                self.data[id].pop(0) # Remove first element
                #without program crashing, it should not go on forever
                #program should goes on until the end of the time (100) 
            curve.setData(self.data[id]) # Sets the data for the curve
        self.my_label.setText(self.yazdir()) # Updates the status label  

    def closeEvent(self, event):
        self.running = False # Setting the program to not running
        super(BandwidthTracker, self).closeEvent(event) # Closing the program

if __name__ == '__main__': # for running the program 
    app = QtWidgets.QApplication(sys.argv) # Creates a Qt application
    mainWin = BandwidthTracker() # Creates a Graph object
    mainWin.show() # Shows the Graph object in the interface
    sys.exit(app.exec_()) # Exits the application when it is closed
