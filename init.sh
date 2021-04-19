#!/usr/bin/env bash
"""
    Setup script to configure environment.

    Note: Update the USER_SHELL according to your preference. {.bashrc, .zshrc, .profile}

    Author: Philipp Rothenhäusler, Stockholm 2021
"""

USER_SHELL=".zshrc"
TBA=()

# Expose repository shells to system path
pylevel_COMMENT="# Pylevel setup"
TBA_COMMENT="${pylevel_COMMENT}"
echo -e "\nAdd shell comment \n\t ${TBA_COMMENT}"
TBA+=("${TBA_COMMENT}")

# Expose repository shells to system path
pylevel_DIR="$(readlink -m "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd )")"
TBA_pylevel_DIR="export pylevel_DIR=${pylevel_DIR}"
echo -e "\nExpose level set toolchain directory: \n\t ${TBA_pylevel_DIR}"
TBA+=("$TBA_pylevel_DIR")

# Expose python package pylevel to PYTHONPATH (for development installation)
TBA_pylevel_PYTHON="export PYTHONPATH=\${pylevel_DIR}:\${PYTHONPATH}"
echo -e "\nExpose pylevel Python package: \n\t ${TBA_pylevel_PYTHON}"
TBA+=("$TBA_pylevel_PYTHON")

# Display current pending additions to .zshrc
echo -e "\nElements to be added to ${USER_SHELL}:"
declare -p TBA

for i in "${TBA[@]}"
do
    if grep -Fxq "$i" ~/$USER_SHELL; then echo -e "\nSkip entry: \n $i";
    else echo "$i" >> ~/$USER_SHELL; echo -e  "\nAdded entry: \n $i"; fi
done


