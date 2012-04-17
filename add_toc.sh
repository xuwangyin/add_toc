#!/bin/bash

markdown user_guide.md > user_guide.html
./add_toc.py user_guide.html user_guide_toc.html
chromium-browser user_guide_toc.html
