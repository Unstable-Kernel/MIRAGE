# Sandbox and Checkpoint Revalidation

This example contains a checkpoint that can be revalidated without resuming any workflow. The default registry includes `run_simulation@0.1`, but the default policy does not permit simulation. The first command therefore reports structured issues, while the second uses an explicit simulation policy and local backend allow-list.

```bash
mirage checkpoint-revalidate examples/06-sandbox-checkpoint/review-checkpoint.json
mirage checkpoint-revalidate examples/06-sandbox-checkpoint/review-checkpoint.json --allow-simulation --backend local
```

Use the sandbox inspection command to distinguish a declarative local test envelope from a required OS-enforced budget:

```bash
mirage sandbox-assess
mirage sandbox-assess --max-memory-mb 256
```

Neither command starts a simulator, resumes a checkpoint, creates a subprocess, or changes host resource settings.
