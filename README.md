# cme_project
This is the project for robotic application for chemical engineering

There are many python executable file in this project:

`operate.py`: this is the main file in this project. Execute this file to process the whole project.

`config.json `: is the file stored parameters, such as where place the glass initially, where is the spin coater ... and so on.

the below file is for robotic arm to function in sequently: 

`start_copy_2.py`: this file executes the initial step, including moving to the initial place, grabbing the glass from the designned place, moving to the top of the spin coater to place the glass on it.

`up.py`: After placing the glass onto the spin coater, the robot arm need to leave the spin coater away along the z axis (meaning increasing the height), and it is what this file processes.

`move.py`: this files instructs the arm to the pre-photo-taking place

`armtest2.py`: it instructs the arm to the photo-taking place, and taking the photo to localizate what rotated angle does glass have with image recognization. After determine the rotated angle, arm will rotate specific angle to grab the glass from the spin coater appropriately.

`putglass.py`: after done the whole process, it will instruct arm to place the glass at the designated place 

`wherePlaceTheGlass.py`: At the beginning, user may not know where to place the glass. This file will go to the initial glass-placing place to show user where do he/she places the glass.

The Below is to control the spin coater
`spinui.py`: this is to press the bottom from computer for controlling spin coater, to set the vac or spin time and mode.

`spinopen.py`: this code is to operate the spin coater, purely rotating the rotator. It is unable to set how long it will rotate, but need to set those parameters in advance by `spinui.py` or other ways.
