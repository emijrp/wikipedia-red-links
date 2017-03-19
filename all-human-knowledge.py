# This script is deprecated
# New one: https://github.com/emijrp/wikidata/blob/master/all.human.knowledge.py

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2016 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import time
import urllib

import pywikibot

def main():
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, 'User:Emijrp/All human knowledge')
    
    wtext = page.text
    newtext = page.text
    autolists = re.findall(r'https://tools.wmflabs.org/autolist/index\.php\?wdq=.*?&run=Run', wtext)
    
    for autolist in autolists:
        time.sleep(1)
        autolist_ = autolist + '&chunk_size=100'
        print(autolist_)
        
        try:
            f = urllib.request.urlopen(autolist_)
            html = f.read().decode('utf-8')
            num = re.findall(r'<p>Getting WDQ data\.\.\. ([\d\,]+) items loaded.</p>', html)[0]
            num = re.sub(',', '', num)
            print(num)
        except:
            print('Error retrieving',autolist_)
            continue
        
        autolist_r = re.sub(r'\?', '\?', autolist)
        newtext = re.sub(r'\[%s \d+\]' % (autolist_r), '[%s %s]' % (autolist, num), newtext)
    
    if wtext != newtext:
        pywikibot.showDiff(wtext, newtext)
        page.text = newtext
        page.save('BOT - Updating figures')
    
if __name__ == '__main__':
    main()
