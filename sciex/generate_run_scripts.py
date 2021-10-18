# Generate scripts to run all experiment trials
import argparse
import sys
import sciex
import os
import pickle

exp_path = "./"

def main():
    parser = argparse.ArgumentParser(description="Generate run_*.sh scripts")
    parser.add_argument("-p", "-E", "-P", "-e", "--exp-path", type=str,
                        default="./", help="Path to root directory of the experiment. Default (recommended): './'")
    parser.add_argument("-s", "--splits", type=int, default=5,
                        help="Number of run scripts to split the trials")
    parser.add_argument("-T", "--timeout", type=str,
                        help="The amount of time allowed to run each trial."
                        "For example '20m' means 20 minutes; '5s' means 5 seconds."
                        "Refer to the man page of the `timeout` command for time formatting")
    args = parser.parse_args()

    # load trials
    trials = []
    split = int(args.splits)
    for trial_name in os.listdir(args.exp_path):
        if not os.path.isdir(os.path.join(exp_path, trial_name)):
            continue
        print("Loading {}".format(trial_name))
        with open(os.path.join(exp_path, trial_name, "trial.pkl"), "rb") as f:
            trial = pickle.load(f)
        trials.append(trial)

    print("Generating run scripts...")
    sciex.Experiment.GENERATE_TRIAL_SCRIPTS(exp_path,
                                            trials,
                                            prefix="run",
                                            exist_ok=True,
                                            split=split,
                                            timeout=args.timeout)

if __name__ == "__main__":
    main()
