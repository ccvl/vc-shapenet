# vc-shapenet
ShapeNet rendering scripts for visual concept

## Install
- Download `ShapeNetCore.v1.zip` to this folder. 

    Unzip the zip file, the folder structure will looks like `ShapeNetCore.v1/02691156/[model_id]`. `model_id` is a very long string and is the unique id for a model.
    
- Setup code from RenderForCNN

    - `git submodule init` and `git submodule update` to get `RenderForCNN` code into the `rendercnn` folder.
    
    - mv `global_variables.py.example` to `global_variables.py` and change the configuration for blender
    
    Notice: The dependency on RenderForCNN is quite heavy and not necessary at all. we can consider get rid of it.

## Scripts in this repository

- render_airplane.py

    Batch script to render all airplane model, use the viewpoint file in `viewpoints` folder
        
- view_3d_model.py
    
    Take `[model_id]` as its input argument. Show this 3D model in blender. 
    
- show_preview.py
    
    Generate an html file containing rendered images.
    
## Other code

- blender_script.py

    The code to be executed in blender, responsible for setting up camera, loading model, etc.
    
- render_opt.py
    
    Rendering configuration code, such as lighting, etc.
    
## Viewpoint
The viewpoint is saved in `viewpoints/` folder.

    
# vc-shapenet_v2
In addition to Weichao's code, render all categories of more view angles from ShapeNet.hhhh

## Install
In addition to Weichao's, I recommend adding GNU-parallel module to speed up rendering process(OPTIONAL).
``` 
sudo apt-get parallel
```

## Scripts added

- render_all.py

    Batch script to render all all models from all categories, use `the all_views.txt` file in `viewpoints` folder
        
- blender_all.py
    
    Fixing the lighting problem in previous blender script  
    
- name.txt
    
    Listing the name of categories

## Run the Code
1. In root folder, run
```
python render_all.py

```
After a few minites, you will see render_commands.txt in the root folder.

2. In root folder, run
```
parallel < render_commands.txt
```

    This takes about 8 days to run in 12 cores in parallel. If you don't want it in parallel, run render commands as shell scripts.

##Output

    Images will be populated in ROOT_FOLDER/images/. The filename convention is [category_id]_[model_id]_a[azimuth]_e[elevation]_t[tilt]_d[distance].png.
    
