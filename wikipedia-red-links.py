#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2014 emijrp <emijrp@gmail.com>
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

import MySQLdb
import re
import sys

def main():
    project = "WikiProject_Feminism_articles"
    limit = 1000000
    if len(sys.argv) > 1:
        project = sys.argv[1]
    if len(sys.argv) > 2:
        limit = int(sys.argv[2])
    query = "SELECT pl_title, count(*) AS count FROM pagelinks WHERE pl_namespace=0 AND pl_from IN (SELECT page_id FROM page WHERE page_namespace=0 AND page_title IN (SELECT page_title FROM categorylinks, page WHERE cl_from=page_id AND page_namespace=1 AND cl_to='%s')) AND pl_title NOT IN (SELECT page_title FROM page WHERE page_namespace=0) GROUP BY pl_title ORDER BY count DESC LIMIT %s;" % (project, limit)
    
    conn = MySQLdb.connect(host='s1.labsdb', db='enwiki_p', read_default_file='~/replica.my.cnf', charset="utf8", use_unicode=True)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    l = []
    for row in result:
        pl_title = re.sub('_', ' ', unicode(row[0], 'utf-8'))
        count = row[1]
        l.append([pl_title, count])
    cursor.close()
    conn.close()
    
    c = 1
    output = u"""{| class="wikitable sortable"
! # !! Red link !! Links"""
    for redlink, count in l:
        output += u"\n|-\n| %s || [[%s]] || [[Special:WhatLinksHere/%s|%s]] " % (c, redlink, redlink, count)
        c += 1
    output += u"\n|}"
    print output.encode('utf-8')

if __name__ == '__main__':
    main()
