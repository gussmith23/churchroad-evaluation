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
