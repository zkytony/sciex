# Go through every trial directory, unpickle the trial.pkl,
# then based on RESULT TYPES, collect the results for each
# trial. Organize them by trial name.

import os
import pickle
from sciex.components import Trial

EXPERIMENT_PATH = os.path.dirname(os.path.abspath(__file__))

def main():
    results = {}  # result_type -> {global_name -> {specific_name -> {seed -> actual_result}}}

    # First iteration, collect trial objects
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

        # We expect one root (trial directory) contains one trial.pkl.
        if not os.path.exists(os.path.join(root, "trial.pkl")):
            print("Warning: trial.pkl not found in %s" % os.path.join(root))
            continue  # just skip this directory
        with open(os.path.join(root, "trial.pkl"), "rb") as f:
            trial = pickle.load(f)

        result_types = type(trial).RESULT_TYPES
        for result_type in result_types:
            if result_type not in results:
                results[result_type] = {}
            if global_name not in results[result_type]:
                results[result_type][global_name] = {}
            if specific_name not in results[result_type][global_name]:
                results[result_type][global_name][specific_name] = {}

            result_file = result_type.FILENAME()
            # get the file of this result time
            if os.path.exists(os.path.join(root, result_file)):
                result = result_type.collect(os.path.join(root, result_file))
                results[result_type][global_name][specific_name][seed] = result
            else:
                print("Warning: %s result file %s not found in %s" % (str(result_type), result_file, os.path.join(root)))
        print("Collected results in %s" % trial_name)

    gathered_results = Trial.gather_results(results)
    for result_type in gathered_results:
        output_file = result_type.save_gathered_results(gathered_results[result_type], EXPERIMENT_PATH)
        if output_file is not None:
            print("Result %s gathered and saved in %s." % (str(result_type), output_file))
        else:
            print("Nothing to be saved for %s" % result_type)


if __name__ == "__main__":
    main()
