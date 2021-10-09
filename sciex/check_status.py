"""
Reports status of currently running experiment. This script
is copied with experiment trials are generated. For example:

$ python check_status.py

Experiment Status (09/10/2021 21:55:23):
     Total: 720
  Finished: 80 (11.1%)

You can provide the path to a shell script, for example, a
run script that contains trial_runner commands or one that
actually contains sourcing multiple run scripts. And this
program will collect the names of the trials and check whether
they are complete. You can also provide prefix multiple
run scripts with that prefix will be processed.

The criteria for completion is simple - whether 'config.yaml'
exists in the trial's folder. Because every trial must have
config and the config is only saved when the trial finishes
and the results are reported.
"""
import argparse
import pickle
import os
import yaml
from datetime import datetime as dt

EXPERIMENT_PATH = os.path.dirname(os.path.abspath(__file__))

def trial_completed(trial_path):
    if os.path.exists(os.path.join(trial_path, "config.yaml")):
        # The trial has completed, because the config file is saved,
        # and at least there is one other file in the directory
        if len(os.listdir(trial_path)) > 2:
            return True
    return False


def load_trial_names_in_run_script(runscript_path):
    results = []
    with open(runscript_path) as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if "python trial_runner.py" in line:
            line = line[line.index("python trial_runner.py"):]
            trial_path = line.split()[2]
            if trial_path.startswith("\""):
                trial_path = trial_path[1:-1]
            results.append(os.path.basename(os.path.dirname(trial_path)))
        elif line.startswith("source"):
            inner_runscript_path = line.split()[1]
            results.extend(load_trial_names_in_run_script(inner_runscript_path))

    return results


def main():
    parser = argparse.ArgumentParser(description="Check experiment status")
    parser.add_argument("-P", "--run-script-path", type=str, default="",
                        help="Path to a shell script that"
                        "contains clues for figuring out which"
                        "trials the shell script covers")
    parser.add_argument("--prefix", type=str, default="",
                        help="Prefix to run script files. This will override the -P option")
    args = parser.parse_args()

    trials_to_check = []
    if args.prefix is not None:
        for fname in os.listdir(EXPERIMENT_PATH):
            if not os.path.isdir(os.path.join(EXPERIMENT_PATH, fname)):
                if fname.startswith(args.prefix) and fname.endswith("sh"):
                    filepath = os.path.join(EXPERIMENT_PATH, fname)
                    trials_to_check.extend(load_trial_names_in_run_script(filepath))
    else:
        if len(args.run_script_path) > 0:
            filepath = os.path.join(EXPERIMENT_PATH, args.run_script_path)
            trials_to_check.extend(load_trial_names_in_run_script(filepath))


    status = {
        "finished": 0,
        "total": 0
    }

    for fname in os.listdir(EXPERIMENT_PATH):
        if not os.path.join(EXPERIMENT_PATH, fname, "trial.pkl"):
            continue
        if not os.path.isdir(os.path.join(EXPERIMENT_PATH, fname)):
            continue

        trial_name = fname
        if (len(args.run_script_path) > 0\
            or len(args.prefix) > 0)\
            and trial_name not in trials_to_check:
            continue

        if len(trial_name.split("_")) == 2:
            global_name, specific_name = trial_name.split("_")
            seed = "no_seed"
        elif len(trial_name.split("_")) == 3:
            global_name, seed, specific_name = trial_name.split("_")
        else:
            print("Skipping trial %s due to invalid trial name format" % (trial_name))
            continue

        if trial_completed(os.path.join(EXPERIMENT_PATH, trial_name)):
            status["finished"] += 1
        status["total"] += 1

    time_str = dt.now().strftime("%m/%d/%Y %H:%M:%S")
    print("Experiment Status (%s):" % time_str)
    if len(args.prefix) > 0:
        print("       For: {}".format(args.prefix))
    elif len(args.run_script_path) > 0:
        print("       For: {}".format(args.run_script_path))
    print("     Total: {}".format(status["total"]))
    print("  Finished: {} ({:.1%})".format(status["finished"],
                                           status["finished"]/max(1,status["total"])))

if __name__ == "__main__":
    main()
