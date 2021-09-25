"""
Divide running scripts by computers. This is useful
for the case where you have generated a lot of running
scripts (each runs multiple trials) and you want to
add another level of grouping.
"""
import math
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Divide run scripts by computers")
    parser.add_argument("exp_path", type=str, help="path_to_experiment")
    parser.add_argument("-c", "--computers",
                        type=str, nargs="+", help="computers to run",
                        default=[os.uname()[1]])
    parser.add_argument("-n", "--num-terminals", type=int, nargs="+",
                        help="Number of parallel terminals for running experiments on each computer",
                        default=[1])
    parser.add_argument("-r", "--ratios", type=float, nargs="+",
                        help="ratio all run scripts to run on each computer; e.g. -r 0.1 0.5 0.3 0.1. The default is even",
                        default=[1.0])
    parser.add_argument("--prefix", type=str, help="prefix to run scripts", default="run")
    args = parser.parse_args()

    run_scripts = []
    for fname in os.listdir(args.exp_path):
        fullpath = os.path.join(args.exp_path, fname)
        if os.path.isdir(fullpath):
            continue

        if fname.startswith(args.prefix) and fname.endswith(".sh"):
            run_scripts.append(fname)

    # Verify argument lengths
    assert len(args.computers) == len(args.num_terminals) == len(args.ratios),\
        "arguments to --computers, --num-terminals, --ratios must have the same length"

    # First, divide the run scripts by computers according to ratio
    ratio_sum = sum(args.ratios)
    ratios = [args.ratios[i] / ratio_sum for i in range(len(args.ratios))]
    _by_computers = {}
    begin = 0
    end = 0
    for i in range(len(args.computers)):
        computer = args.computers[i]
        ratio = ratios[i]
        if end <= begin:
            end += int(math.ceil(ratio*len(run_scripts)))
            end = min(len(run_scripts), end)
        print("{} will take {}:{}".format(computer, begin, end))
        _by_computers[computer] = run_scripts[begin:end]
        begin = end

    # Then, divide the computer run scripts by num_parallel, evenly
    _by_terminals = {computer: []
                     for computer in _by_computers}
    for i, computer in enumerate(_by_computers):
        scripts = _by_computers[computer]
        num_terminals = args.num_terminals[i]
        for j in range(num_terminals):
            batchsize = int(math.ceil(len(scripts) / num_terminals))
            begin = j*batchsize
            if begin >= len(scripts):
                break
            end = min((j+1)*batchsize, len(scripts))

            print("Generating script for trials [%d-%d] (computer=%s, split=%d)" % (begin+1, end, computer, j))
            shellscript_path = os.path.join(args.exp_path,
                                            "group_{}_{}.sh".format(computer, j))
            with open(os.open(shellscript_path, os.O_CREAT | os.O_WRONLY, 0o777), "w") as f:
                for script in scripts[begin:end]:
                    f.write("source {}\n".format(script))

if __name__ == "__main__":
    main()
