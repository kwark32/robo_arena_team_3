#!/usr/bin/python

# Imports
import sys
from PyQt5.QtWidgets import QApplication, QWidget


# Main function
def main():

    # Get QT Application
    app = QApplication(sys.argv)

    # Get screen and resolution from it
    screen = app.primaryScreen()
    width = screen.size().width()
    height = screen.size().height()

    # Create window as QWidget
    w = QWidget()
    # Resize and move window dynamically
    w.resize(int(width/2), int(height/2))
    w.move(int(width/4), int(height/4))
    # Set window title
    w.setWindowTitle('RoboArena')
    # Make the window visible
    w.show()

    # Exit when window is closed
    sys.exit(app.exec_())


# Run main, and only if we want it to run
if __name__ == '__main__':
    main()
