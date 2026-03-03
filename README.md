# robotframework-ibmmq

**Robot Framework keywords for IBM MQ — powered by the `ibmmq` Python package.**

This library is a **thin, explicit Robot Framework wrapper around the `ibmmq` Python package**.
It does **not** abstract away IBM MQ complexity — and that is **by design**.

If you use this library, you are using **real IBM MQ**, with **real native dependencies**, exactly like production.

---

## What this library is (and is not)

✅ **IS**
- A Robot Framework library for **connecting to IBM MQ**
- A wrapper around the **`ibmmq` Python package**
- Designed for **real integration testing**, not mocks or file-based substitutes

❌ **IS NOT**
- A pure-Python library
- A “just pip install and go” solution
- A fake or simulated MQ implementation

If you are looking for something that avoids native dependencies, **this library is not for you**.

---

## 🚨 Read this first: IBM MQ prerequisites are mandatory

This library **directly depends on `ibmmq`**, which is a **Python extension module backed by IBM MQ native libraries**.

> **If `ibmmq` does not work on your machine, this Robot Framework library will not work either.**

Before you do *anything else*, you **must** read and follow the official `ibmmq` prerequisites:

👉 **Official ibmmq prerequisites (REQUIRED):**  
https://github.com/ibm-messaging/mq-mqi-python?tab=readme-ov-file#prerequisites

### In practical terms, this means:

You **must have**, on the machine where tests run:

- ✅ IBM MQ C Client
- ✅ IBM MQ SDK
- ✅ A working C/C++ build toolchain
- ✅ Correct environment variables (e.g. `MQ_FILE_PATH` if MQ is not installed in the default location)

If any of the above is missing, you will see errors such as:

- `ModuleNotFoundError: No module named 'ibmmqc'`
- DLL load failures
- Import errors during `pip install` or at runtime

These are **environment issues**, not bugs in this library.

---

## Platform notes

- ✅ Windows: Supported
- ✅ Linux: Supported
- ❌ No native MQ installation = no support

On Windows, a proper **Visual C++ build environment is required**, because `ibmmq` includes native extensions.

---

## Installation

### Step 1 — Verify `ibmmq` works first (strongly recommended)

```bash
python -c "import ibmmq; print('ibmmq OK')"
```

If this fails, **stop here** and fix your IBM MQ / `ibmmq` installation first.

### Step 2 — Install this library

```bash
pip install robotframework-ibmmq
```

No magic. No hidden installers.

---

## Usage example

```robot
*** Settings ***
Library    IBMMQLibrary

*** Test Cases ***
Connect to IBM MQ
    Connect MQ
    ...    queue_manager=QM_EXAMPLE
    ...    hostname=mq.example.internal
    ...    port=1414
    ...    channel=SYSTEM.ADMIN.SVRCONN
    ...    username=${NONE}
    ...    password=${NONE}

    Disconnect All MQ Connections
```

This connects to a **real queue manager** using a **real MQ channel**.

---

## MQ administration notes

If required:

- Ensure the MQ channel exists and is running
- Ensure the MQ listener is active
- Common admin channel: `SYSTEM.ADMIN.SVRCONN`

Use **IBM MQ Explorer** or platform tooling to manage this.

---

## Troubleshooting

Errors mentioning `ibmmqc`, DLL load failures, or missing shared libraries are **IBM MQ / ibmmq environment problems**.

Re-check:
- IBM MQ installation
- `ibmmq` prerequisites
- Environment variables
- 32-bit vs 64-bit mismatches

Official reference:
https://github.com/ibm-messaging/mq-mqi-python?tab=readme-ov-file#prerequisites

---

## Acknowledgements ❤️

**Special thanks to UWV** for sponsoring, supporting, and **open-sourcing** this library.

By funding real-world test tooling and releasing it as open source, UWV has contributed back to the broader Robot Framework and IBM MQ communities.
