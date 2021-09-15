"""
Filter trials.
"""
import pickle
import argparse
import os
import sys
from sciex.components import Trial, Experiment
from sciex.check_status import trial_completed

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

def filter_empty(args):
    os.makedirs(args.output_path, exist_ok=True)
    trials_to_copy = []
    for fname in os.listdir(args.exp_path):
        fullpath = os.path.join(args.exp_path, fname)
        if not os.path.isdir(fullpath):
            continue

        trial_name = os.path.basename(fname)
        if Trial.verify_name(trial_name):
            if trial_completed(fullpath):
                continue
            else:
                with open(os.path.join(fullpath, "trial.pkl"), "rb") as f:
                    trial = pickle.load(f)
                trials_to_copy.append(trial)
                sys.stdout.write("{} is not completed. Will include.\n".format(trial.name))
                sys.stdout.flush()

    # Generate a new experiment based on these trials
    exp = Experiment(args.output_exp_name,
                     trials_to_copy,
                     args.output_path)
    exp.generate_trial_scripts(split=int(args.num_splits),
                               exist_ok=True,
                               evenly=True)

def main():
    parser = argparse.ArgumentParser(description="Filter Trials")
    parser.add_argument("exp_path", type=str, help="path to the experiment root directory")
    parser.add_argument("-o", "--output-path", type=str, help="path to directory to store the filtered trials")
    parser.add_argument("-n", "--output-exp-name", type=str, help="Name to the new experiment that contains the filtered trials",
                        default="FilteredExperiment")
    parser.add_argument("-s", "--num-splits", type=str,
                        help="Number of splits. Default is 4", default=4)
    parser.add_argument("-E", "--filter-empty",
                        help="Filters empty trials, i.e. trials that do not have results",
                        action="store_true")
    args = parser.parse_args()

    if args.filter_empty:
        filter_empty(args)

if __name__ == "__main__":
    main()
