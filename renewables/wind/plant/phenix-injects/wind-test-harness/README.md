# Wind Cyber Hardening Attack Harness

The Attack Test Harness (ATTAR) was developed by INL and published at
[https://github.com/IdahoLabUnsupported/ATTAR](https://github.com/IdahoLabUnsupported/ATTAR).

This version of the attack harness is designed to evaluate the security of
different wind site cybersecurity tools by launching different representative
attacks on the simulated infrastructure.

# Test Harness Details

## Version

`v1.0.0`

## Description

The test harness is a tool designed to run processes and validate that the
process has ran. It is meant to be used remotely and distributes the test
scripts via SSH, it also runs and returns the results of the script via SSH. To
avoid typing passwords ssh keys are used, and can be installed automatically
using the `hosts.sh` script which will be explained later. In a nutshell what
the test harness does is transfer scripts laid out in a CSV file to a host
specified in a `hosts.csv` file and runs them piping all the results to the
original location, after which it runs a second script to test the results and
ensure they are as expected.

It is important to understand the user need not understand how `main.sh` works,
users only need to know how to create test scripts and add them to the list in
`tests.csv`.

Everything is based on the strong naming convention, all that needs to be done
for `main.sh` to work is the test scripts need to be named exactly as they are
defined in `tests.csv`, see below for more details.

## Example

As a simple example the Eternal Blue attack will be demonstrated. This example
will explain every step of the process as the attack runs and is validated. This
assumes that the eternal blue attack is the only one listed in the `tests.csv`
file.

1. User runs `main.sh` from a location that can reach a Kali VM
1. `main.sh` reads `tests.csv` to see which test it should run
1. `main.sh` uses `hosts.sh` to get username and ip of target where test will run
1. `main.sh` uses secure copy (SCP) to move `attackvm1_eternalblue1.sh` to
`root@172.16.100.250:/tmp`
1. `main.sh` runs the script it just transferred in (step #4) piping the output
locally to `attackvm1_eternalblue.txt`
1. `main.sh` checks to see if `attackvm1_eternalblue.txt` exists, if so it runs
`attackvm1_eternalblue1_test.sh`
1. `attackvm1_eternalblue1_test.sh` checks the output of
`attackvm1_eternalblue.txt` for the 'WIN' text result is piped to
`attackvm1_eternalblue1_test.txt`
1. `main.sh` moves onto the next test in `tests.csv` if it exists

## Quick Start, Test Creation

This is a quick guide to explain how to create a new test. In this example we
assume everything else is already setup and the test harness is being ran on a
compute node while there is a Kali VM accessible at the same address as in the
example above.

1. Add test to `tests.csv` in this format, in a new line at the bottom.

```
attackvm1;eternalblue2;another eb;
```

2. Create a script to be ran on the Kali VM, and another to validate the first
script's output

```
touch attackvm1_eternalblue2.sh; touch attackvm1_eternalblue2_test.sh: chmod +x *.sh
```

3. Add code to `attackvm1_eternalblue2.sh` as desired, this code will run on the
Kali VM in `/tmp`
4. Add code to `attackvm1_eternalblue2_test.sh` to check the output from
`attackvm1_eternalblue2.txt` and return a 'TEST PASS' or 'TEST FAIL' exactly
like in `attackvm1_eternalblue1_test.sh`. In fact
`attackvm1_eternalblue1_test.sh` can be copied and simply changed on line8 to
look at `eternalblue2`

## Naming Convention

In the `tests.csv` the format is as follows:

```
{host};{name};{note};

host: name of a host defined in 'hosts.csv'
name: unique name of test
note: can be anything assuming it is alphanumeric, avoid any other chars
```

These same variables from `tests.csv` are used to know which scripts to copy and
run, as well as what to name the output from the scripts.

The script that will be pushed to the host and run should be named like this:

```
{host}.{name}.sh
```

And the script that will be ran locally that consumes the output of the previous
script should be named like this:

```
{host}.{name}_test.sh
```

In the `hosts.csv` the format is as follows:

```
{host};{username};{ip}

host:     unique hostname used to look up this host, matched off of what's in
          tests.csv
username: username to use (user will have to type password if SSH key's missing)
ip:       IP address to use to push the scripts and run them
```