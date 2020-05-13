import os
import pickle
from sciex import Experiment

def add_baseline(baseline_name,
                 path_to_experiment,
                 trial_func,
                 save_trials=False,
                 split=4):
    """
    Given an experiment folder that possibly already contain,
    add a baseline to run on some of the same configurations.
    
    Args:
        trial_func (function): A function that maps from
            (global_name, seed, config (dict)) to a Trial object.
        save_trials (bool): True if you want to save the baseline trials.
        split (int): If save_trials is True, this will be the number of splits
            the saved trials will be divided into, and shell scripts will be generated
            to run each split.
        baseline_name (str): Name of the baseline
    """
    if not os.path.isabs(path_to_experiment):
        raise ValueError("Path to experiment must be absolute path.")

    combinations = set({})
    new_trials = []
    
    for root, dirs, files in os.walk(path_to_experiment):
        # root: top-level directory (recursive)
        # dirs: direct subdirectories of root
        # files: files directly under root.
        if root == path_to_experiment:
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

        if (global_name, seed) in combinations:
            continue

        # Read the trial object and obtain the configuration
        if not os.path.exists(os.path.join(root, "trial.pkl")):
            print("Warning: trial.pkl not found in %s" % os.path.join(root))
            continue  # just skip this directory
        with open(os.path.join(root, "trial.pkl"), "rb") as f:
            trial = pickle.load(f)

        baseline_trial = trial_func(global_name, seed, trial.config)
        assert baseline_trial.global_name == global_name, "Global name of baseline trial not matching."
        assert baseline_trial.seed == seed, "Seed of baseline trial not matching."

        if save_trials:
            # Save the trial
            trial_path = os.path.join(path_to_experiment, baseline_trial.name)
            if not os.path.exists(trial_path):
                os.makedirs(trial_path)
            with open(os.path.join(trial_path, "trial.pkl"), "wb") as f:
                pickle.dump(baseline_trial, f)
                
        new_trials.append(baseline_trial)
        print("Added baseline trial for %s_%s" % (global_name, str(seed)))
        combinations.add((global_name, seed))

    if save_trials:
        Experiment.GENERATE_TRIAL_SCRIPTS(path_to_experiment,
                                          new_trials,
                                          prefix="run_%s" % baseline_name,
                                          split=split)
    return new_trials
