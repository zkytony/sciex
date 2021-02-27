import pickle
import os
import yaml
from datetime import datetime as dt

EXPERIMENT_PATH = os.path.dirname(os.path.abspath(__file__))

def main():

    status = {
        "finished": 0,
        "total": 0
    }

    for root, dirs, files in os.walk(EXPERIMENT_PATH):
        # root: top-level directory (recursive)
        # dirs: direct subdirectories of root
        # files: files directly under root.
        if root == EXPERIMENT_PATH:
            continue

        trial_name = os.path.basename(root)
        if len(trial_name.split("_")) == 2:
            global_name, specific_name = trial_name.split("_")
            seed = "no_seed"
        elif len(trial_name.split("_")) == 3:
            global_name, seed, specific_name = trial_name.split("_")
        else:
            print("Skipping trial %s due to invalid trial name format" % (trial_name))
            continue

        if os.path.exists(os.path.join(root, "config.yaml")):
            # The trial has completed, because the config file is saved.
            status["finished"] += 1
        status["total"] += 1

    time_str = dt.now().strftime("%m/%d/%Y %H:%M:%S")
    print("Experiment Status (%s):" % time_str)
    print("     Total: {}".format(status["total"]))
    print("  Finished: {} ({:.1%})".format(status["finished"],
                                           status["finished"]/status["total"]))

if __name__ == "__main__":
    main()
