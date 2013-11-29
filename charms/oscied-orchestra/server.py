#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://github.com/ebu/PlugIt

import plugit
import actions

if __name__ == "__main__":
    plugit.load_actions(actions)
    plugit.app.run(debug=plugit.params.DEBUG)
