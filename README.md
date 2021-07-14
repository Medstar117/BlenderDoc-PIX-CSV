# BlenderDoc PIX CSV
A Blender plugin for importing model data from PIX CSV formatted files generated by RenderDoc. This is a stand-alone fork of Stanislav Bobovych's "import_pix.py" script, which is part of his "Game Tools" repository. I have my own reasons for wanting to do this; but one can, for example, do things from seeing how one's 3D model is being rendered in a given application (aka, debugging why their model is looking all janky) or to making a STL file of their favorite 3D model from a game or whatnot more effectively.

I only say this one thing if you choose to use this plugin--**don't be stupid.** Don't go around stealing assets from different games and such for your own personal gain (i.e. don't go around making models and such from games and making money off of it--that's highly illegal). If you're wanting to do it for a personal, non-commercial project, so be it; but if you get in trouble with the authorities or with whomever you stole assets from, that's on **you**. I hold no responsibility for you using this plugin like that.

Please heed the above warning. Be smart.

Original repository of script: https://github.com/sbobovyc/GameTools

My fork of the original repository: https://github.com/Medstar117/GameTools

## Details to note
The original script was made for Blender 2.7.8. The goal is to port this plugin to work with Blender 2.83.3. The following checklist details the goals of this project:

- [X] Get the plugin to work with Blender 2.83.3 LTS (meshes only)
- [X] Clean up script of leftover/debuging data
- [X] Configure script to be more dynamic in data retrieval (i.e. don't make the script assume that a specific column will have a certain piece of data every time)
- [X] Fix normals importing
- [X] Fix UV importing
- [ ] Add bone importing
- [ ] Add Tangent importing
- [ ] Add Binormal importing

...

## Before you use...
When grabbing the CSV data for a model in RenderDoc, you need to grab both the input CSV data **AND** the output CSV data. The main file you need is the input CSV data; **HOWEVER**, you need to replace a_TexCoord0.x and a_TexCoord0.y in the input CSV file with v_Varying0.x and v_Varying0.y from the output CSV file respectively. Keep the a_TexCoord0 names at the top of the columns of the file you're modifying--DON'T do a direct copy-paste that replaces the columns' names.

In short, **DO** replace the **DATA** for "a_TexCoord0.x" and "a_TexCoord0.y" with "v_Varying0.x" and "v_Varying0.y" respectively. **DON'T** replace the literal words "a_TexCoord0.x" and "a_TexCoord0.y" with "v_Varying0.x" and "v_Varying0.y"!

## How to use

### For the old 2.7.8 script:
1. Open Blender
2. Select the "File" tab at the top left of the window
3. Select User Preferences
4. Select the "Add-ons" tab in the new window that pops up
5. Select the "Install from File..." button at the bottom of the window
6. Navigate to where the "import_pix.py" file is located
7. Double click the script or press the "Install from File..." button at the top right of the window
8. Select the "Community" button under "Supported Level" and the "User" button to display the plugin
9. Ensure that the checkbox for the plugin is set to be enabled/ has a checkmark in it
10. The option to import PIX CSV files should now be under the "File > Import" menu

### For the new 2.80.0/ 2.83.3 LTS script:
1. Open Blender
2. Select the "Edit" tab at the top left of the window
3. Select "Preferences..."
4. Press the "Install..." button at the top right of the window
5. Navigate to where the "import_pix_csv.py" file is located
6. Double click the script or press the "Install Add-on..." button at the bottom right of the window
7. Ensure that the checkbox for the plugin is set to be enabled/ has a checkmark in it
8. The option to import PIX CSV files should now be under the "File > Import" menu
