from datetime import datetime as dt
import concurrent.futures
import traceback
import os

class Event:
    NORMAL = "Normal"
    WARNING = "Warning"
    ERROR = "Error"
    SUCCESS = "Success"

    def __init__(self, description, kind=Event.Normal, time=dt.now()):
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
    def __init__(self, name, trials, outdir, logging=True):
        self.name = name
        self.trials = trials
        self._outdir = outdir
        self._logging = logging

    def begin(self, max_workers=61):
        results = []
        start_time = dt.now()
        start_time_str = start_time.strftime("%Y%m%d%H%M%S%f")[:-3]
        try:
            if not parallel:
                result = trials.run()
                results.append(result)
            else:
                # Can at most run max_workers number of trials in parallel.
                # So have to split up trial running in batches.
                last_n = 0
                for n in range(1, len(self.trials), max_workers):
                    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
                        results = executor.map(self._run_single, list(self.trials[last_n:n]))
                    last_n = n
        except Exception as ex:
            print("Experiment fialed to complete due to Exception")
            traceback.print_exc()
        finally:
            for trial_name, result, log in results:
                trial_path = os.path.join(self._outdir, "%s_%s" % (trial_name, start_time_str))
                if not os.path.exists(trial_path):
                    os.makedirs(trial_path)
                print("Saving results for trial %s at %s..." % (trial_name, result_path))                    
                result_path = os.path.join(trial_path, result.filename)
                result.save(result_path)
                
                if self._logging:
                    log_path = os.path.join(trial_path, "log.txt")
                    with open(log_path, "wb") as f:
                        print("| Saving events to %s..." % (log_path))
                        for event in log:
                            f.write(str(event))

    def _run_single(self, trial):
        result = trial.run(logging=self._logging)
        return trial.name, result, trial.log

    
class Trial:
    def __init__(self, name, config):
        self.config = config
        self.name = name
        self._log = []

    def run(self, logging=False):
        """Returns a Result object"""
        raise NotImplemented

    def log_event(self, event):
        """May be called during trial.run()"""
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


