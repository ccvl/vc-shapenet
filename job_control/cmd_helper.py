import db_info
import argparse
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd_file')
    parser.add_argument('--image-set', help='The image set to check which commands are unfinished.')
    parser.add_argument('--unfinished', action='store_true', help='Output unfinished tasks')
    parser.add_argument('--split', type = int, default = 1, help='No split by default')
    # parser.add_argument('output', help='The output filename')

    args = parser.parse_args()
    
    cmd_set = db_info.RenderCmdSet(args.cmd_file)

    image_set = None
    if args.image_set:
        image_set = db_info.ImageSet(args.image_set)

    if args.unfinished and image_set:
        _, fully_completed_cmd_set = cmd_set.unfinished(image_set, img_per_obj_instance=1000)
        print 'Full Completed %d' % len(fully_completed_cmd_set)
        less_than_900, _ = cmd_set.unfinished(image_set, img_per_obj_instance=900)
        print 'Less than 900 %d' % len(less_than_900)
        less_than_800, _ = cmd_set.unfinished(image_set, img_per_obj_instance=800)
        print 'Less than 800 %d' % len(less_than_800)
        less1, _ = cmd_set.unfinished(image_set, img_per_obj_instance=1)
        print 'Completely missing %d' % len(less1)


