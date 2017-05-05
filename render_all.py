import os, sys, tempfile, shutil
import glob
import global_variables as G
import os.path as osp
import numpy as np
# set debug mode
debug_mode = 0
if debug_mode:
    io_redirect = ''
else:
    io_redirect = ' > /dev/null 2>&1'

# import blender configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR,'../'))
# from global_variables import *

def call_blender(modelfile, catogory):
    '''
    This function is modified from render_class_view.py
    '''
    blank_file = osp.join(G.g_blank_blend_file_path)
    # render_code = osp.join(g_render4cnn_root_folder, 'render_pipeline/render_model_views.py')
    # The render code is customized from render_model_view.py
    render_code = 'blender_all.py'


    temp_dirname = tempfile.mkdtemp()

    view_file = 'viewpoints/all_views.txt'
    shape = modelfile.split('/')[9]
    shape_synset = modelfile.split('/')[8]
    syn_images_folder = os.path.join('images', catogory)
    render_cmd = '%s %s -noaudio --background --python %s -- %s %s %s %s %s >> report_all' % (
        G.g_blender_executable_path,
        blank_file,
        render_code,
        modelfile,
        shape_synset,
        shape,
        view_file,
        syn_images_folder
    )
    try:
        #f = open('render_commands.txt','a')
        print G.g_blender_executable_path,
        f= open(shape_synset,'a')
        f.write(render_cmd+'\n')
        f.close()        
        #os.system('%s' %render_cmd)
        #imgs = glob.glob(temp_dirname+'/*.png')
        #shutil.move(imgs[0], output_img)
    except Exception as e:
        print e
        print('render failed. render_cmd: %s' % (render_cmd))

    # CLEAN UP
    shutil.rmtree(temp_dirname)


if __name__ == '__main__':
    # List models
    import glob
    f = open('name.txt','r')
    lines = f.readlines()
    for line in lines:
        category = line[0:8]
        model_dir = os.path.join(G.g_shapenet_root_folder, category, '*/models/model_normalized.obj')
        print model_dir 
        models = glob.glob(model_dir)
       # k = open('count.txt','a')
       # k.write(str(len(models)*84) + ' ' + line)
       # k.close()
        models = np.random.choice(models, 10)
        for model_file in models:
            print 'here'
            call_blender(model_file)
	    print model_file
            #call_blender(model_file, category)

