# Reproduce the run_*.sh scripts
# by reorganizing the commands in existing scripts
# into new scripts (with shuffle or not) and the
# user can specify how many run_*.sh scripts to produce
# and a suffix after "run_".

import argparse
import os
import math
import random

def main():
    parser = argparse.ArgumentParser(description="reorganize trial running commands in shell scripts.")
    parser.add_argument("num_out_scripts", type=int,
                        help="Number of trial running shell scripts to produce;"\
                        "Note: The generated amount may not exactly match this number, for balancing")
    parser.add_argument("suffix", help="Suffix to the generated shell script names, in the format of run_{suffix}_{number}.sh")
    parser.add_argument("--exp-path", type=str,
                        help="path to experiment root (that contains all trials)."\
                        "Default is current directory", default="./")
    parser.add_argument("--shuffle", action="store_true",
                        help="Shuffle the trials again")
    parser.add_argument("--prefix", default="run_",
                        help="Prefix to the existing .sh running scripts. Default 'run_'.")
    args = parser.parse_args()

    all_lines = []
    for filename in os.listdir(args.exp_path):
        if os.path.isdir(os.path.join(args.exp_path, filename)):
            continue  # skip directories

        if filename.startswith(args.prefix):
            with open(os.path.join(args.exp_path, filename)) as f:
                content = f.readlines()
                all_lines.extend(content)

    if args.shuffle:
        random.shuffle(all_lines)

    lines_per_script = int(math.ceil(len(all_lines) / args.num_out_scripts))
    for i in range(args.num_out_scripts):
        begin = i*lines_per_script
        if begin >= len(all_lines):
            break
        end = min((i+1)*lines_per_script, len(all_lines))

        lines = all_lines[begin:end]
        run_script_filepath = os.path.join(args.exp_path, "run_{}_{}.sh".format(args.suffix, i))
        with open(run_script_filepath, "a") as f:
            f.writelines(lines)
            print(run_script_filepath)
        os.chmod(run_script_filepath, 0o775)


if __name__ == "__main__":
    main()
