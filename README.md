# Churchroad Evaluation

Evaluation for the Churchroad project.

```sh
git clone <this repo>
cp .env.template .env
# Fill in the fields of .env as needed

# Do this every time you're working on the project or running the eval.
source .env

pip install -r requirements

# Should print a bunch of experiment tasks
doit list --all

# Run the evaluation. 
./run-evaluation.sh

# Can also run `doit` directly, though run-evaluation.sh is more tuned for performance.
doit
```

## Development Notes

As of June 2025, we use a self-hosted runner that Gus set up on Google Cloud Platform. The setup of that machine was fairly simple but is not documented in this repo anywhere, so I document it here. It is a fairly standard Ubuntu VM on which I installed the GitHub Runners service. I also added a large disk to store Vivado and whatever experimental data we generate.
