import argparse, math
parser = argparse.ArgumentParser()
parser.add_argument('render_commands')
parser.add_argument('--nodes', type=int, default=7)

args = parser.parse_args()

with open(args.render_commands) as f:
     lines = f.readlines()

N = len(lines)
step = int(math.ceil(N / float(args.nodes)))


for idx in range(args.nodes):
    start_idx = step * idx
    split_lines = lines[start_idx : start_idx + step]
    with open('split_%d.txt' % idx, 'w') as f:
        f.writelines(split_lines)

     
