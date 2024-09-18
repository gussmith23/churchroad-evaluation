import subprocess
from tempfile import NamedTemporaryFile
from time import time
import pandas as pd
import matplotlib.pyplot as plt
import util
import plotly.express as px 


def _impl_mul_verify_timeout_experiment():

    manifest = util.get_manifest()
    timeout = manifest["mul_verify_experiment_timeout"]

    # records containing {bitwidth, time, timed_out}
    results = []
    solvers = ["bitwuzla", "z3", "cvc5", "yices", "stp"]

    for solver in solvers:
        for bw in [2, 4, 6, 8, 10, 12, 14, 16]:
            source = f"""#lang rosette
    (require rosette/solver/smt/z3)
    (require rosette/solver/smt/bitwuzla)
    (require rosette/solver/smt/cvc5)
    (require rosette/solver/smt/yices)
    (require rosette/solver/smt/stp)
    (current-solver ({solver}))
    (define bw {bw}) ; Larger bitwidths begin to time out!
    (define-symbolic a1 a0 b1 b0 (bitvector (/ bw 2)))
    (define a (concat a1 a0))
    (define b (concat b1 b0))
    (verify (assert
    (bveq (bvmul a b)
        (bvadd 
            (bvmul (zero-extend a0 (bitvector bw)) 
                (zero-extend b0 (bitvector bw)))
            (bvshl (zero-extend (bvmul a0 b1) (bitvector bw))
                (bv (/ bw 2) bw))
            (bvshl (zero-extend (bvmul a1 b0) (bitvector bw))
                (bv (/ bw 2) bw))))))
    """

            tempfile = NamedTemporaryFile(suffix=".rkt", delete=False)
            tempfile.write(source.encode())
            tempfile.flush()

            p = subprocess.Popen(
                ["racket", tempfile.name],
                # check=True,
                # timeout=timeout,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            start = time()
            try:
                p.communicate(timeout=timeout)
                runtime = time() - start
                timed_out = False
            except subprocess.TimeoutExpired:
                runtime = time() - start
                p.terminate()
                timed_out = True

            results.append({"solver": solver,
                            "bitwidth": bw, 
                            "time": runtime, 
                            "timed_out": timed_out})

    df = pd.DataFrame(results)

    output_path = util.output_dir() / "figures" / "mul_verify_timeout_experiment.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)


    fig = px.bar(df, 
                 x='bitwidth', 
                 y='time', 
                 color='solver', 
                 barmode='group', 
                 text='solver',
                 width=5*96,
                 height=4*96) # 96 pixels <-> 1 in
    fig.update_layout(xaxis_title='Bitwidth',
                      yaxis_title='Solver Time',
                      title='Time to Solve Multiply Operation')
    fig.write_image(output_path)


def task_mul_verify_timeout_experiment():
    return {
        "actions": [_impl_mul_verify_timeout_experiment],
        "targets": [util.output_dir() / "figures" / "mul_verify_timeout_experiment.png"],
    }
