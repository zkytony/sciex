import argparse
import pickle
import os
import yaml

def main():
    parser = argparse.ArgumentParser(description='Run a trial.')
    parser.add_argument("pickle_file", type=str,
                        help="Path to trial pickle file")
    parser.add_argument("exp_path", type=str,
                        help="Path to experiment root")
    parser.add_argument("--logging", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.pickle_file):
        print("{} not found".format(args.pickle_file))
        return

    with open(args.pickle_file, "rb") as f:
        trial = pickle.load(f)

    if os.path.exists(os.path.join(args.exp_path, trial.name, "config.yaml")):
        print("Skipping {} because it seems to be done".format(trial.name))
        return

    # run trial
    results = trial.run(logging=args.logging)
    save_trial_results(args.exp_path, trial.name, results, trial.log, trial.config)

def save_trial_results(exp_path, trial_name, trial_results, log, config):
    trial_path = os.path.join(exp_path, trial_name)
    if not os.path.exists(trial_path):
        os.makedirs(trial_path)

    config_path = os.path.join(trial_path, "config.yaml")
    print("Saving configuration for trial %s at %s..." % (trial_name, config_path))
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    print("Saving results for trial %s..." % (trial_name))
    for result in trial_results:
        result_path = os.path.join(trial_path, result.filename)
        result.save(result_path)

    log_path = os.path.join(trial_path, "log.txt")
    with open(log_path, "w") as f:
        print("| Saving events to %s..." % (log_path))
        for event in log:
            f.write(str(event) + "\n")

if __name__ == "__main__":
    main()
