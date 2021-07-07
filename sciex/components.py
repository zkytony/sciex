from datetime import datetime as dt
import concurrent.futures
import traceback
import os
import shutil
import yaml
import pickle
import math
from pprint import pprint
import sciex.util as util

ABS_PATH = os.path.dirname(os.path.abspath(__file__))

class Event:
    NORMAL = "Normal"
    WARNING = "Warning"
    ERROR = "Error"
    SUCCESS = "Success"

    def __init__(self, description, kind="Normal"):
        self._description = description
        self._kind = kind
        self._time = dt.now()

    def __str__(self):
        return "%s Event (%s): %s" % (str(self._time), self._kind, self._description)

    def __repr__(self):
        return str(self)


class Experiment:
    """One experiment simply groups a set of trials together.
    Runs them together, manages results etc."""
    def __init__(self, name, trials, outdir,
                 logging=True, verbose=False, add_timestamp=True):
        """
        outdir: The root directory to organize all experiment results.
        """
        if add_timestamp:
            start_time = dt.now()
            start_time_str = start_time.strftime("%Y%m%d%H%M%S%f")[:-3]
            self.name = "%s_%s" % (name, start_time_str)
        else:
            self.name = name
        self.trials = trials
        self._outdir = outdir
        self._logging = logging
        self._trial_paths = {}  # map from trial path to set{(result_type, result_filename)...}
        for t in trials:
            t.verbose = verbose

    def generate_trial_scripts(self, prefix="run", split=4, exist_ok=False, evenly=True):
        Experiment.GENERATE_TRIAL_SCRIPTS(os.path.join(self._outdir, self.name),
                                          self.trials, prefix=prefix, split=split,
                                          exist_ok=exist_ok, evenly=evenly)

    @classmethod
    def GENERATE_TRIAL_SCRIPTS(cls, exp_path,
                               trials, prefix="run", split=4, exist_ok=False, evenly=True):
        """Generate shell scripts to run trials."""
        os.makedirs(exp_path, exist_ok=exist_ok)
        # Dump the pickle files
        for trial in trials:
            trial_path = os.path.join(exp_path, trial.name)
            trial.trial_path = trial_path
            if not exist_ok and os.path.exists(os.path.join(trial_path, "trial.pkl")):
                print("sciex: trial.pkl for %s already exists" % (trial.name))
                continue
            if not os.path.exists(trial_path):
                os.makedirs(trial_path)
            with open(os.path.join(trial_path, "trial.pkl"), "wb") as f:
                pickle.dump(trial, f)

        # copy runner script
        shutil.copyfile(os.path.join(ABS_PATH, "trial_runner.py"),
                        os.path.join(exp_path, "trial_runner.py"))

        # Generate shell scripts
        if evenly:
            print("Will split trials EVENLY with probably fewer total splits.")
            batchsize = int(math.ceil((len(trials) / split)))
        else:
            print("Will split trials EXACTLY with given total splits"\
                  "but the last split may contain more trials.")
            batchsize = len(trials) // split

        for i in range(split):
            begin = i*batchsize
            if begin >= len(trials):
                break
            end = min((i+1)*batchsize, len(trials))

            print("Generating script for trials [%d-%d] (split=%d)" % (begin+1, end, i))
            shellscript_path = os.path.join(exp_path, "%s_%d.sh" % (prefix, i))
            with open(os.open(shellscript_path, os.O_CREAT | os.O_WRONLY, 0o777), "w") as f:
                for trial in trials[begin:end]:
                    if os.path.isabs(exp_path):
                        dirpath = exp_path
                    else:
                        dirpath = "./"
                    f.write("python trial_runner.py \"%s\" \"%s\" --logging\n"
                            % (os.path.join(dirpath, trial.name, "trial.pkl"),
                               os.path.join(dirpath)))

        # Copy gather results script
        shutil.copyfile(os.path.join(ABS_PATH, "gather_results.py"),
                        os.path.join(exp_path, "gather_results.py"))

        # Copy check status script
        shutil.copyfile(os.path.join(ABS_PATH, "check_status.py"),
                        os.path.join(exp_path, "check_status.py"))


class Trial:

    # Set this to be a list of strings or tuples (as key-chain in dictionary)
    # used in verifying config.
    REQUIRED_CONFIGS = []

    def __init__(self, name, config, verbose=False):
        """
        Trial name convention: "{trial-global-name}_{seed}_{specific-setting-name}"

        Example: gridworld4x4_153_value-iteration-200.

        The ``seed'' is optional. If not provided, then there should be only one underscore.
        """
        # Verify name format
        if len(name.split("_")) != 2 and len(name.split("_")) != 3:
            raise ValueError("Name format\n  \"%s\"\nincorrect (Check underscores)" % name)
        elif len(name.split("_")) == 3:
            global_name, seed, specific_name = name.split("_")
            try:
                int(seed)
            except ValueError:
                raise ValueError("seed _%s_ is not an integer" % seed)
            self.global_name = global_name
            self.seed = seed
            self.specific_name = specific_name
        elif len(name.split("_")) == 2:
            self.global_name, self.specific_name = name.split("_")
            self.seed = None

        errors = self._verify_config(config)
        if len(errors) > 0:
            print("Errors:")
            pprint(errors)
            raise ValueError("Invalid configuration.")

        self.name = name
        self._config = config
        self._log = []
        self.verbose = verbose
        # The path to the directory where the results of this trial should be saved.
        # This is usually set by the Experiment when it is generating scripts to
        # run the trials.
        self.trial_path = None

    @property
    def config(self):
        return self._config

    def run(self, logging=False):
        """Returns a list of Result objects"""
        raise NotImplemented

    def log_event(self, event):
        """May be called during trial.run()"""
        if self.verbose:
            print(str(event))
        self._log.append(event)

    @property
    def log(self):
        return self._log

    @classmethod
    def gather_results(cls, results):
        """Given a dictionary produced by `gather_results.py`
        of the format result_type -> {global_name -> {specific_name -> {seed -> actual_result}}},
        return a gathered result of each result type"""
        gathered_results = {}
        for result_type in results:
            gathered_results[result_type] = {}
            for global_name in results[result_type]:
                gr = result_type.gather(results[result_type][global_name])
                if gr is None:
                    continue
                gathered_results[result_type][global_name] = gr
        return gathered_results

    def _verify_config(self, config):
        """
        Returns:
            A list of error messages in string
        """
        errors = []
        for entry in self.__class__.REQUIRED_CONFIGS:
            if type(entry) == str:
                if entry not in config:
                    errors.append("Missing configuration for '{}'".format(entry))
            elif type(entry) == tuple:
                if entry[0] not in config:
                    errors.append("Missing configuration for '{}'".format(entry))
                dct = config[entry[0]]
                key_chain = [entry[0]]
                for key in entry[1:]:
                    key_chain.append(key)
                    if key not in dct:
                        errors.append("Missing configuration for '{}'".format(",".join(key_chain)))
                    dct = dct[key]
        return errors

class Result:
    @classmethod
    def collect(cls, path):
        """path can be a str of a list of paths"""
        raise NotImplemented

    @classmethod
    def FILENAME(cls):
        """If this result depends on only one file,
        put the filename here"""
        raise NotImplemented

    @classmethod
    def FILENAMES(cls):
        """Returns a list of filenames the result depends on"""
        return [cls.FILENAME()]

    def save(self, path):
        """Save result to given path to file"""
        raise NotImplemented

    @property
    def filename(self):
        return type(self).FILENAME()

    @classmethod
    def gather(cls, results):
        """`results` is a mapping from specific_name to a dictionary {seed: actual_result}.
        Returns a more understandable interpretation of these results"""
        return None

    @classmethod
    def save_gathered_results(cls, results, path):
        """results is a mapping from global_name to the object returned by `gather()`.
        Post-processing of results should happen here.
        Return "None" if nothing to be saved."""
        return None
