#!/usr/bin/python3
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

import pwb
import pywikibot
import re
import sys
import urllib

def convertOccupation(oc):
    if oc.lower() == 'actor':
        return 'actress'
    return oc

def main():
    limit = 0
    country = ''
    localwiki = ''
    if len(sys.argv) >= 2:
        localwiki = sys.argv[1]
    if len(sys.argv) >= 3:
        country = sys.argv[2]
    if len(sys.argv) >= 4:
        limit = int(sys.argv[3])
    if len(sys.argv) <= 1:
        print('Use: python script.py LOCALWIKI COUNTRYNAME LIMIT')
        sys.exit()
    
    site = pywikibot.Site('en', 'wikipedia')
    repo = site.data_repository()
    people = []
    
    countryids = []
    if country.lower() == 'africa':
        url = 'https://tools.wmflabs.org/autolist/index.php?language=en&project=wikipedia&category=&depth=12&wdq=claim[31%3A6256]%20claim[30%3A15]&pagepile=&statementlist=&run=Run&mode_manual=or&mode_cat=or&mode_wdq=not&mode_find=or&chunk_size=1000&download=1'
        f = urllib.request.urlopen(url)
        countryids = f.read().strip().splitlines()
        countryids.remove(b'Q142')
        countryids.remove(b'Q29')
        print('Loaded',len(countryids),'countries')
    else:
        page = pywikibot.Page(site, country)
        item = pywikibot.ItemPage.fromPage(page)
        countryids = [item.getID().encode()]
    print('Analysing',countryids)
    
    salir = False
    skip = []
    for countryid in countryids:
        if salir:
            break
        
        countryitem = pywikibot.ItemPage(repo, countryid.decode("utf-8"))
        countryitem.get()
        if localwiki in countryitem.labels:
            countryname = countryitem.labels[localwiki]
        else:
            countryname = countryitem.labels['en']
        print('#'*50,'\n',countryname,countryid,'\n','#'*50,'\n')
        if countryid in skip:
            print('Skiping...')
            continue
        
        url2 = 'https://tools.wmflabs.org/autolist/index.php?language=en&project=wikipedia&category=&depth=12&wdq=claim[21%%3A6581072]%%20claim[27%%3A%s]&pagepile=&statementlist=&run=Run&mode_manual=or&mode_cat=or&mode_wdq=not&mode_find=or&chunk_size=%s&download=1' % (countryid.decode("utf-8")[1:], limit*2)
        f = urllib.request.urlopen(url2)
        personids = f.read().strip().splitlines()
        print('AutoList returned',len(personids),'results')
        
        for personid in personids:
            person = {'q': '', 'name': '-', 'birth': '', 'death': '', 'occupation': [], 'image': '', 'commons': ''}
            personitem = pywikibot.ItemPage(repo, personid.decode("utf-8"))
            try:
                personitem.get()
            except:
                continue
            
            if localwiki+'wiki' in personitem.sitelinks.keys():
                print('\n',personid,'exists in',localwiki,'wiki, skiping',personitem.sitelinks)
                continue
            
            person['sitelinks'] = personitem.sitelinks
            if 'commonswiki' in person['sitelinks']:
                person['commons'] = person['sitelinks']['commonswiki']
                person['sitelinks'].pop('commonswiki')
            if not list(person['sitelinks'].keys()):
                continue
            print('\n',person['sitelinks'])
            
            person['q'] = personid
            person['name'] = personitem.sitelinks[list(person['sitelinks'].keys())[0]]
            for k in list(person['sitelinks'].keys()): #we prefer names in latin chars
                if not re.search(r'(?im)[a-z]', person['name']) and re.search(r'(?im)[a-z]', k):
                    person['name'] = k
            
            if personitem.claims:
                if 'P18' in personitem.claims:
                    image = personitem.claims['P18'][0].getTarget()
                    if image.fileIsOnCommons():
                        print('Image:', image.title())
                        person['image'] = image.title()
                if 'P106' in personitem.claims:
                    for p106 in personitem.claims['P106']:
                        ocitem = p106.getTarget()
                        try:
                            ocitem.get()
                            if localwiki in ocitem.labels:
                                oc = convertOccupation(ocitem.labels[localwiki])
                                print('Occupation:', oc)
                                person['occupation'].append(oc)
                            elif 'en' in ocitem.labels:
                                oc = convertOccupation(ocitem.labels['en'])
                                print('Occupation:', oc)
                                person['occupation'].append(oc)
                            else:
                                pass
                        except:
                            pass
                if 'P569' in personitem.claims:
                    birth = personitem.claims['P569'][0].getTarget()
                    if birth:
                        birthdate = '%04d-%02d-%02d' % (birth.year, birth.month, birth.day)
                        if birthdate != '2000-01-01':
                            print('Birth:', birthdate)
                            person['birth'] = birthdate
                if 'P570' in personitem.claims:
                    death = personitem.claims['P570'][0].getTarget()
                    if death:
                        deathdate = '%04d-%02d-%02d' % (death.year, death.month, death.day)
                        if deathdate != '2000-01-01':
                            print('Death:', deathdate)
                            person['death'] = deathdate
            people.append([countryname, person['name'], person])
            if limit > 0 and len(people) >= limit:
                salir = True
                break
    
    try:
        people.sort()
    except:
        pass
    headercontinent = '! # !! Name !! Occupation !! Birth !! Death !! Country !! Image !! Iw\n'
    headercountry = '! # !! Name !! Occupation !! Birth !! Death !! Image !! Iw\n'
    tablebegin = '{| class="wikitable sortable"\n'
    tableend = '|}'
    output = ['', ]
    i = 0
    output[i] = tablebegin
    
    if country.lower() == 'africa':
        output[i] += headercontinent
    else:
        output[i] += headercountry
    
    c = 0
    tablelimit = 1000
    for person in people:
        c += 1
        if c >= tablelimit and c % tablelimit == 1:
            output[i] += tableend
            i += 1
            output.append('')
            output[i] = tablebegin
            if country.lower() == 'africa':
                output[i] += headercontinent
            else:
                output[i] += headercountry
        
        interwiki = ', '.join(['[[:%s:%s|%s]]' % (k.split('wiki')[0], v, k.split('wiki')[0]) for k, v in person[2]["sitelinks"].items()])
        
        if country.lower() == 'africa':
            output[i] += '|-\n| %s || [[%s]] <small>(%s)</small> || %s || %s || %s || [[%s]] || %s%s || [[:d:%s|%s]]\n' % (c, person[1], interwiki, person[2]["occupation"] and ', '.join(person[2]["occupation"]) or 'unknown', person[2]["birth"] and person[2]["birth"] or 'unknown', person[2]["death"] and person[2]["death"] or '-', person[0], person[2]["image"] and '[[%s|80px]]' % person[2]["image"] or '-', person[2]['commons'] and '<br/>[[:commons:%s|Commons]]' % person[2]['commons'], person[2]['q'].decode("utf-8"), len(person[2]['sitelinks']))
        else:
            output[i] += '|-\n| %s || [[%s]] <small>(%s)</small> || %s || %s || %s || %s%s || [[:d:%s|%s]]\n' % (c, person[1], interwiki, person[2]["occupation"] and ', '.join(person[2]["occupation"]) or 'unknown', person[2]["birth"] and person[2]["birth"] or 'unknown', person[2]["death"] and person[2]["death"] or '-', person[2]["image"] and '[[%s|80px]]' % person[2]["image"] or '-', person[2]['commons'] and '<br/>[[:commons:%s|Commons]]' % person[2]['commons'], person[2]['q'].decode("utf-8"), len(person[2]['sitelinks']))
    
    output[i] += tableend
    print('\n'.join(output))
    print('Found',len(people),'missing biographies')
    
    #save in file
    f = open('missing-bios-%s-%s.txt' % (localwiki.lower(), country.lower()), 'w')
    f.write('\n'.join(output))
    f.close()
    
    #save in wiki
    ensite = pywikibot.Site('en', 'wikipedia')
    if len(output) == 1:
        page = pywikibot.Page(ensite, 'User:Emijrp/sandbox')
        page.text = '{{Wikipedia:WikiProject Women/Women in Red/Missing articles by nationality/header|1=%s}}\n\n%s\n\n{{Wikipedia:WikiProject Women/Women in Red/Missing articles by nationality/footer}}' % (country, output[0])
        page.save(u'table')
    else:
        c = 1
        for outputsplit in output:
            page = pywikibot.Page(ensite, 'User:Emijrp/sandbox')
            page.text = '{{Wikipedia:WikiProject Women/Women in Red/Missing articles by nationality/header|1=%s|2=%s}}\n\n%s\n\n{{Wikipedia:WikiProject Women/Women in Red/Missing articles by nationality/footer}}' % (country, c, outputsplit)
            page.save(u'table')
            c += 1

if __name__ == '__main__':
    main()
