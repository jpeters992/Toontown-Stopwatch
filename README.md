**TOONTOWN REWRITTEN STOPWATCH**

Use this to time your runs in any cog facility while you do the boss fight or run a factory, mint, office, or cog golf course! This is still a work in progress, so some things may not work.

**Usage**

1. Create a folder on the desktop
2. Insert all files from the repository inside the folder
3. Open Powershell and navigate to the directory of your folder where you stored the files
4. Run "python main_gui.py".
5. The tkinter window should pop up
6. Notice the tabs on top and the modes
7. Select what facility you are in and the desired mode
8. Sellbot: Press the start button whenever before you enter the factory. The stopwatch will not start until you enter the factory and it sees "Entrance Room" at the top of the screen. The stopwatch will start once the room is detected.
9. Cashbot: Press the start button whenever before you enter the mint. The stopwatch will not start until you enter the mint and it detects what floor you are on. For this, press F2 to display the debug information (Note: The code is set for my region on where "Floor: [number]" is detected. You may have to change this on your end. To do this: 1. open Cashbot_tab.py 2. CTRL+F and type "bbox" 3. Look at the values and change to your need. The first 2 values determine the top left corner of the box and the other 2 values determine the right corner of the box. Use Microsoft Paint to determine the position, hover your cursor on the top left of "Floor" and bottom right of the number. The bottom left corner will show you your pixels, input those into the bbox values (x1, y1, x2, y2)). The stopwatch will start when the floor is detected.
10. Lawbot: Press the start button whenever beforee you enter the office. The stopwatch will not start until you enter the office and it detects what floor you are on. For this, press F2 to display the debug information. The stopwatch will start when the floor is detected.
11. Bossbot: Work In Progress


**How it works**

1. Once the image is found, the stopwatch will begin.
2. There are splits to show you timestamps of your time, these work by using battle detection. Make sure to not obstruct visual of the shticker book as the program uses exact image match.
3. When you enter battle, the book disappears and the program detects this.
4. After finishing the battle, the book reappears and the program detects this. A timestamp will be made.
5. At the end of your run, the text at the top under the player's name (4x or 2x) Bonus will be read to detect the end.
6. Your times will be saved automatically to a .json file that appears within the folder.

**Known issues**

1. The program fails to capture the end of your run.
2. If you hover over the shitcker book, this will make a timestamp once you stop hovering over it.
3. Lawbot has not been tested.
4. Bossbot has not been implemented.
