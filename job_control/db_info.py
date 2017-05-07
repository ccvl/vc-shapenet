import argparse
import glob, os, sys, json

class RenderCmdSet:
    '''
    Render commands is on the object instance level, which is much smaller than image level
    '''
    def __init__(self, data):
        self.command_lines = [] 
        self.obj_categories = [] 
        self.obj_instances = [] 
        if type(data) is str: # filename
            filename = data
            with open(filename) as f:
                command_lines = f.readlines()
        elif type(data) is list:
            command_lines = data
        else:
            assert False, 'Unknown input type %s for RenderCmdSet' % type(data)
            
        self._parse_commands(command_lines)

    def __len__(self):
        return len(self.command_lines)

    def __str__(self):
        return '\n'.join(self.command_lines) 

    def _parse_commands(self, command_lines):
        if not command_lines or len(command_lines) == 0:
            print('Warning: the cmd_set is empty')
            return

        self.command_lines = command_lines 
        commands = [l.split(' ') for l in command_lines]
        self.obj_categories = [v[8] for v in commands]
        self.obj_instances = [v[9] for v in commands]

        assert len(self.obj_categories[0]) == 8 
        assert len(self.obj_instances[0]) == 32

    def unfinished(self, image_set, img_per_obj_instance):
        # Exclude finished commands
        unfinished_command_lines = []
        finished_command_lines = []
        for i in range(len(self.command_lines)):
            command_line = self.command_lines[i]
            category = self.obj_categories[i]
            instance_id = self.obj_instances[i]
            if image_set.data.get(category)  \
                    and image_set.data[category].get(instance_id) \
                    and len(image_set.data[category][instance_id]) >= img_per_obj_instance:
                    # This command is done
                finished_command_lines.append(command_line)
                continue
            else:
                unfinished_command_lines.append(command_line)
        return RenderCmdSet(unfinished_command_lines), RenderCmdSet(finished_command_lines)


class ImageSet:
    '''
    Quickly get a summary about the image set
    '''
    def __init__(self, root):
        if root.endswith('.json'):
            buf = json.load(open(root))
            self.root = buf['root']
            self.data = buf['data']
        else:
            self.root = root
            # Data is a two-level dictionary
            # data[category_name] = instances
            # instances[instance_name] = images
            self.data = {} 
            self._iter_sub_folders() # Load data

    def dump(self, json_file):
        '''
        Dump data to a json file
        '''
        buf = dict(root = self.root, data = self.data)
        with open(json_file, 'w') as f:
            json.dump(buf, f)

    def summary(self, category=True, instance=True):
        '''
        Print a summary of this image set
        How many images for each 
        '''
        db_total = 0
        for (k,v) in self.data.iteritems():
            instances = v
            if category:
                category_total = sum([len(im_list) for _, im_list in instances.iteritems()])
                db_total += category_total
                print 'Category %s, Object# %d, Images# %d' % (k, len(v), category_total)
            
            if instance:
                for (k, v) in instances.iteritems():
                    print '    Object %s, Image# %d' % (k, len(v))
        print 'Total images in the root folder %d' % db_total

    def progress_summary(self, images_per_obj, category_list=None):
        '''
        Print a summary of this image set
        How many images for each 
        '''
        for (k,v) in self.data.iteritems():
            if category:
                print 'Category %s, Object# %d, Images# %d' % (k, len(v), sum([len(im) for im in v]))
            
            
    def _iter_sub_folders(self):
        listdir = os.listdir(self.root)
        subfolders = [v for v in listdir if os.path.isdir(os.path.join(self.root, v))]

        n = len(subfolders)
        for i in range(n):
            subfolder = subfolders[i]
            assert len(subfolder) == 8, 'Folder %s should not be in the data folder %s' % (subfolder, root)
        
            sys.stdout.write('\rParsing folder %s, %d/%d' % (subfolder, i, n))
            sys.stdout.flush()

            self._parse_sub_folder(subfolder)
        sys.stdout.write('\n')
    
        return subfolders

    def _parse_sub_folder(self, subfolder):
        self.data[subfolder] = {}

        img_list = glob.glob(os.path.join(self.root, subfolder, '*.png'))
        n = len(img_list)
        # Do I assume the ordering of the file list?
        for img in img_list:
            [category, instance] = self._parse_filename(img)
            
            if not self.data[category].get(instance):
                self.data[category][instance] = []
            self.data[category][instance].append(img)

    def _parse_filename(self, filename):
        '''
        A file looks like this images/02843684/02843684_ff90921e9631cd73c5c86021644af7b5_8_a128_e309_t000_d002.png
        '''
        basename = os.path.basename(filename)
        fields = basename.split('_')
        category, instance = fields[0:2]
        return category, instance


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    parser.add_argument('--dump-json', help='Output to a json file')
    parser.add_argument('--rennder_command') # Render command file

    args = parser.parse_args()

    imageset = ImageSet(args.folder)
    if args.dump_json:
        json_file = args.dump_json
        imageset.dump(json_file)

    imageset.summary(True, False)

