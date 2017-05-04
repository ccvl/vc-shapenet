# only leave the useful commands
with open('render_commands.txt') as f:
    command_lines = f.readlines()
commands = [l.split(' ') for l in command_lines]
obj_categories = [v[7] for v in commands]
obj_instances = [v[8] for v in commands]

obj_cat_set = set(obj_categories)

with open('good_obj_cat.txt') as f:
    lines = f.readlines()
done_obj_cat_set = set([l.strip() for l in lines])
print len(done_obj_cat_set)
print len(obj_cat_set)

missing_obj_cat_set = obj_cat_set - done_obj_cat_set
print len(missing_obj_cat_set)

new_commands = []
ins_counter = 0
cur_category = None 
is_missing = None
num_inst_needed = 64
for i in range(len(commands)):
    if obj_categories[i] != cur_category:
        cur_category = obj_categories[i]
        ins_counter = 0
        is_missing = (cur_category in missing_obj_cat_set)

    if is_missing and ins_counter < num_inst_needed:
        new_commands.append(command_lines[i]) 
        ins_counter += 1

print len(new_commands)
print new_commands[:10]
print 'Category number: %d, Inst needed: %d' % (len(missing_obj_cat_set), num_inst_needed)
with open('render_commands_for_missing.txt', 'w') as f:
    f.writelines(new_commands)
        

# print len(lines)
# print obj_categories[0]
# print obj_instances[0]
