# Generate scripts to run all experiment trials
import sciex
import os
import pickle

SPLIT = 4
exp_path = "./"

def main():
    # load trials
    trials = []
    for trial_name in os.listdir(exp_path):
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
                                            split=SPLIT)

if __name__ == "__main__":
    main()
