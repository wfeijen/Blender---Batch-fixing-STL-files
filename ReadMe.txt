Automated batch repair of corrupt STL files with Blender under Linux

I usually often modify existing 3D print models in OpenSCAD to adapt them to my needs. Unfortunately a lot of designer (I guess mostly using Fusion 360) do not care if their 3D models and the resulting STL files are a valid, solid 3D object. Often files are not manifold, have holes, etc. 
Frankly speaking: The 3D object has holes which should not be there. For 3D printing this is often not really an issue since most slicers either ask you if they shall repair the file or do it on their own. For OpenSCAD importing and processing such a "defect" STL results in errors when you render the final file. There are Windows tools such as Adobe Meshmixer or Microsoft 3D Builder to repair such STLs but things get more complicated if you use Linux as your main OS. Meshmixer runs fine under Wine but it is quite time consuming to process a larger amount of defect STLs. 

Blender on the other hand has the 3D Print Toolbox which you need to enable, import the STL, fix the STL, export the fixed STL.

Well, not really comfortable. So I spinned up ChatGPT and asked for a more automated solution and here we go.

You have to adjust the input and output folder inside the Python script:
input_folder = "~/data/3D Druck/0 - Fix STL/source"
output_folder = "~/data/3D Druck/0 - Fix STL/fixed"

Then simply copy your corrupt STL files into the source folder and start Blender either via Bash command or simply with the included shell script. That is it. Worked like a charm for me even with larger amount of files. If the source STL is not corrupt Blender will simply ignore it.

I am running Xubuntu 24.04 as my main OS. I guess most Blender versions should work with this.
