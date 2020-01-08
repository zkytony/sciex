from datetime import datetime as dt
import concurrent.futures
import traceback
import os
import yaml
import sciex.util as util

class Event:
    NORMAL = "Normal"
    WARNING = "Warning"
    ERROR = "Error"
    SUCCESS = "Success"

    def __init__(self, description, kind="Normal", time=dt.now()):
        self._description = description
        self._kind = kind
        self._time = time

    def __str__(self):
        return "%s Event (%s): %s" % (str(self._time), self._kind, self._description)

    def __repr__(self):
        return str(self)
    

class Experiment:
    """One experiment simply groups a set of trials together.
    Runs them together, manages results etc."""
    def __init__(self, name, trials, logging=True, verbose=False, outdir="results"):
        """
        outdir: The root directory to organize all experiment results.
        """
        self.name = name
        self.trials = trials
        self._outdir = outdir
        self._logging = logging
        self._trial_paths = {}  # map from trial path to set{(result_type, result_filename)...}
        for t in trials:
            t.verbose = verbose

    def begin(self, parallel=False, max_workers=61):
        results = []
        start_time = dt.now()
        start_time_str = start_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        try:
            if not parallel:
                for trial in self.trials:
                    trial_results = trial.run(logging=self._logging)
                    results.append((trial.name, trial_results, trial.log, trial.config))
            else:
                # Can at most run max_workers number of trials in parallel.
                # So have to split up trial running in batches.
                last_n = 0
                for n in range(1, len(self.trials), max_workers):
                    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                        results = executor.map(self._run_single, list(self.trials[last_n:n]))
                    last_n = n
        except Exception as ex:
            print("ERROR: Experiment fialed to complete due to Exception")
            traceback.print_exc()
            raise ex
        finally:
            exp_name = "%s_%s" % (self.name, start_time_str)
            for trial_name, trial_results, log, config in results:
                trial_path = os.path.join(self._outdir, exp_name, trial_name)
                if not os.path.exists(trial_path):
                    os.makedirs(trial_path)
                self._trial_paths[trial_path] = set({})

                config_path = os.path.join(trial_path, "config.yaml")
                print("Saving configuration for trial %s at %s..." % (trial_name, config_path))
                with open(config_path, "w") as f:
                    yaml.dump(config, f)

                print("Saving results for trial %s..." % (trial_name))
                for result in trial_results:
                    result_path = os.path.join(trial_path, result.filename)
                    result.save(result_path)
                    self._trial_paths[trial_path].add((type(result), result_path))
                    
                if self._logging:
                    log_path = os.path.join(trial_path, "log.txt")
                    with open(log_path, "w") as f:
                        print("| Saving events to %s..." % (log_path))
                        for event in log:
                            f.write(str(event) + "\n")
            # also save the result file paths
            with open(os.path.join(self._outdir, exp_name, "paths.yaml"), "w") as f:
                yaml.dump(self._trial_paths, f)


    def _run_single(self, trial):
        trial_results = trial.run(logging=self._logging)
        return trial.name, trial_results, trial.log, trial.config

    def collect_results(self):
        results = {}
        for trial_path in self._trial_paths:
            results[trial_path] = []
            for result_type, result_path in self._trial_paths[trial_path]:
                result = result_type.collect(result_path)
                results[trial_path].append(result)
        return results

    
class Trial:
    def __init__(self, name, config, verbose=False):
        self.name = name
        self._config = config
        self._log = []
        self.verbose = verbose

    @property
    def config(self):
        return self._config

    def run(self, logging=False):
        """Returns a Result object"""
        raise NotImplemented

    def log_event(self, event):
        """May be called during trial.run()"""
        if self.verbose:
            print(str(event))
        self._log.append(event)

    @property
    def log(self):
        return self._log

    
class Result:
    @property
    def filename(self):
        return self._filename

    @classmethod
    def collect(cls, path):
        raise NotImplemented

    def save(self, path):
        """Save result to given path to file"""
        raise NotImplemented    


