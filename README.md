# sciex
Framework for "scientific" experiments (Result organization; Experiment and Trial setup; Baseline Comparisons)

This tool helps strip out the repetitive parts of setting up and running experiments, and lets you focus on writing the logic of trial running and result types. This reduces the stupid errors one may make when running experiments, and makes results organized and gathering statistics convenient.

## Setup
```
pip install sciex
```

## How it works

#### An Experiment consists of trials
In this framework, an `Experiment` consists of a number of `Trial`s. One trial is independent from another.
```python
class Experiment:
    """One experiment simply groups a set of trials together.
    Runs them together, manages results etc."""
    def __init__(self, name, trials, outdir,
                 logging=True, verbose=False):
```

A `Trial` can be initialized by a `name` and a `config`. There is no requirement on the format of `config`; It just needs to be able to be serialized by pickle. Note that we recommend a convention of giving trial names:
```python
class Trial:
    def __init__(self, name, config, verbose=False):
        """
        Trial name convention: "{trial-global-name}_{seed}_{specific-setting-name}"

        Example: gridworld4x4_153_value-iteration-200.

        The ``seed'' is optional. If not provided, then there should be only one underscore.
        """
```
**Your job** is to define a child class of `Trial`, implementing its function `run()`, so that it catersx to your experiment design.

#### Parallel trial running
We want to save time and run trials in parallel, if possible. Thus, instead of directly executing the trials, `Experiment` first saves the trials as `pickle` files in **an organized manner**, then generates __shell scripts__, each bundles a subset of all the trials. The shell script contains commands using `trial_runner.py` to conduct trials. More specifically, the **organized manner** means, the pickle files will be saved under, along with `trial_runner.py`, the shell scripts and `gather_results.py`.
```
./{Experiment:outdir}
    /{Experiment:name}_{timestamp}
        /{Trial:name}
            /trial.pkl
        gather_results.py
        run_{i}.sh
        trial_runner.py
```
Inside the shell script `run_{i}` where `i` is the index of the bundle, you will only find commands of the sort:
```
python trial_runner.py {path/to/trial/trial.pkl} {path/to/trial} --logging
```
Thus, you just need to do
```
$ ./run_{i}.sh
```
on a terminal to execute the trials covered by this shell script. You can open multiple terminals and run all shell scripts together in parallel.


#### Result types

We know that for different experiments, we may produce results of different type. For example, some times we have a list of values, some times a list of objects, sometimes a particular kind of object, and some times it is a combination of multiple result types. For instance, each trial in a image classification task may produce labels for test images. Yet each trial in image segmentation task may produce arrays of pixel locations. We want you to decide what those result types are and how to process them. Hence the `Result` interface (see `components.py`).

To be more concrete, in `sciex`, each `Trial` can produce multiple `Result`s. Trials with the same `specific_name` (see trial naming convention above) will be **gathered** (to compute a statistic). See the interface below:
```python
class Result:

    def save(self, path):
        """Save result to given path to file"""
        raise NotImplemented

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
    ...
```
Basically, you define how to save this kind of result (`save()`), how to collect it, i.e. read it from a file (`collect()`), how to gather a set of results of this kind (`gather()`), for example, computing mean and standard deviation. As an example, `sciex` provides a `YamlResult` type (see `result_types.py`):
```python
import yaml
import pickle
from sciex.components import Result
class YamlResult(Result):
    def __init__(self, things):
        self._things = things
    def save(self, path):
        with open(path, "w") as f:
            yaml.dump(self._things, f)
    @classmethod
    def collect(cls, path):
        with open(path) as f:
            return yaml.load(f)
```
We didn't define the `gather()` and `save_gathered_results()` functions because these are experiment-specific. For example, in a reinforcement learning experiment, I may want to gather rewards as a type of result. Here's how I may implement that. Notice that since I know I will put these results in a paper, my implementation of `save_gathered_results` will be saving a LaTex table in a `.tex` file.
```python
class RewardsResult(YamlResult):
    def __init__(self, rewards):
        """rewards: a list of reward floats"""
        super().__init__(rewards)
    @classmethod
    def FILENAME(cls):
        return "rewards.yaml"

    @classmethod
    def gather(cls, results):
        """`results` is a mapping from specific_name to a dictionary {seed: actual_result}.
        Returns a more understandable interpretation of these results"""
        # compute cumulative rewards
        myresult = {}
        for specific_name in results:
            all_rewards = []
            for seed in results[specific_name]:
                cum_reward = sum(list(results[specific_name][seed]))
                all_rewards.append(cum_reward)
            myresult[specific_name] = {'mean': np.mean(all_rewards),
                                       'std': np.std(all_rewards),
                                       '_size': len(results[specific_name])}
        return myresult


    @classmethod
    def save_gathered_results(cls, gathered_results, path):
        def _tex_tab_val(entry, bold=False):
            pm = "$\pm$" if not bold else "$\\bm{\pm}$"
            return "%.2f %s %.2f" % (entry["mean"], pm, entry["std"])

        # Save plain text
        with open(os.path.join(path, "rewards.txt"), "w") as f:
            pprint(gathered_results, stream=f)
        # Save the latex table
        with open(os.path.join(path, "rewards_latex.tex"), "w") as f:
            tex =\
                "\\begin{tabular}{ccccccc}\n%automatically generated table\n"\
                " ... "
            for global_name in gathered_results:
                row =  "  %s   & %s   & %s     & %s      & %s           & %s\\\\\n" % (...)
                tex += row
            tex += "\\end{tabular}"
            f.write(tex)
        return True
```
Then, after all the results are produced, when you want to gather the results and produce some report of the statistics (or plots), just run

```
$ ./{Experiment:outdir}/{Experiment:name}_{timestamp}/gather_results.py
```
