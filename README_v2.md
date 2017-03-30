# vc-shapenet_v2
In addition to Weichao's code, render all categories of more view angles from ShapeNet.

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
    
    
    
