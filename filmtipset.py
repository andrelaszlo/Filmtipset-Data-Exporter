# This project is licensed under a Creative Commons Attribution-NonCommercial
# 3.0 Unported License available at
# http://creativecommons.org/licenses/by-nc/3.0/
# Permissions beyond the scope of this license may be available at <andre@laszlo.nu>

import re
import getpass
import sys

from math import ceil
from datetime import datetime, date

from browser import Browser

class FilmtipsetLoginError(Exception):
    pass

class FilmtipsetBrowser(Browser):

    def __init__(self):
        super().__init__("nyheter24.se", user_agent=Browser.UA_CHROME)

    def login(self, username, password):
        data = {'name': username, 'pass': password}
        (response, data) = self.request("/filmtipset/login.cgi", method="POST", data = data)
        login_data = {'status': response.status,
                      'location': response.getheader('Location')}
        if login_data['status'] == 302:
            if login_data['location'] == 'main.cgi':
                return True
            elif login_data['location'] == 'main.cgi?login=failure':
                return False
        else:
            print("Unknown login response:", str(login_data))
            return False
   
    def home(self):
        member = None
        (response, data) = self.request("/filmtipset/yourpage.cgi")
        html = str(data, "latin_1")
        nr_match = re.search(r'Medlem nr: ([0-9]+)', html, re.M)
        if nr_match:
            member = int(nr_match.group(1))
        grades = dict()
        for i in range(1,6):
            pattern = 'grade_'+str(i)+'_bg_middle_vert.gif" height="[0-9]*" width="[0-9]*" border="0" alt="([0-9]*)"'
            nr_match = re.search(pattern, html, re.M)
            if nr_match:
                grades[i] = int(nr_match.group(1))
            
        return {'member': member, 'grades': grades}

    def movies(self, member, graded_movies):
        url = "/filmtipset/yourpage.cgi?member=%s&page=show_grades&sort=name&limit=%s&grade=%s&only_unseen=0"
        pattern = r'a href="film/(.*?)\.html".*?Titel:</i></b> (.*?)</div>.*?Originaltitel:</i></b> (.*?)</div>.*?Film nr\.:</i></b> ([0-9]*)</div>.*?Betyg satt:</i></b> (.*?)<br/>'
        info = re.compile(pattern, re.I)
        movies = []
        #for grade in [1]:
        for grade in range(1,6):
            pages = int(ceil(graded_movies[grade]/100.0))
            #for offset in [0]:
            for offset in range(pages):
                print("Loading movies graded %s (page %s of %s)" % (grade, offset+1, pages))
                curl = url % (member, offset*100, grade)
                (response, data) = self.request(curl)
                html = str(data, 'latin_1')
                f = open("./filmtipset-grades.html", 'w')
                f.write(html)
                f.close()
                for line in html.splitlines():
                    match = info.search(line)
                    if match:
                        m_date = date(*[int(x) for x in match.group(5).split('-')])
                        movies.append({'grade': grade,
                                       'url': match.group(1),
                                       'title': match.group(2),
                                       'o_title': match.group(3),
                                       'id': int(match.group(4)),
                                       'date': m_date})
                        #print("%s got grade %s" % (movies[-1]['o_title'], movies[-1]['grade']))
        return movies

    def comments(self, member):
        url = "/filmtipset/yourpage.cgi?page=commented_movies&member=%s&offset=%s"
        pat = re.compile(r'<a href="film/(.*?).html".*?' + 
                         r'<div style="" class=favoritetext>(.*?)</div>.*?' + 
                         r'(\d+):(\d+) (\d+)/(\d+) (\d{4})',
                         re.MULTILINE | re.DOTALL)
        nxt = re.compile(r'images/ner\.gif', re.IGNORECASE | re.MULTILINE)
        comments = []
        offset = 0
        while True: # loop through comment pages
            print("\rComment page %s" % str(int(round(offset/20.0))+1), end="")
            sys.stdout.flush()
            furl = url % (member, offset)
            (response, data) = self.request(furl)
            html = str(data, 'latin_1')
            for m in pat.finditer(html):
                (h, mi, y, mo, d) = map(lambda x: int(m.group(x)),
                                        [3, 4, 7, 6, 5])
                #TODO: Fix timezone (?)
                comments.append((m.group(1), self.decode(m.group(2)), datetime(y, mo, d, h, mi)))
                #print("\n%s:\n'%s'" % (m.group(1), m.group(2)))
            if nxt.search(html):
                offset += 20
            else:
                break # last page
        print()
        return comments

    def imdb(self, url):
        full_url = "/filmtipset/film/%s.html"
        pattern = r'http://www.imdb.com/title/tt([0-9]*)/'
        (response, data) = self.request(full_url % url)
        html = str(data, 'latin_1')
        match = re.search(pattern, html, re.M)
        if match:
            return int(match.group(1))
        else:
            return None

    def load(self, username, password):
        if not self.login(username, password):
            raise FilmtipsetLoginError()
        else:
            h = self.home()
            member = h['member']
            print(username, "is member number", member)
            
            grades = h['grades']
            if grades:
                print("Grades:")
                m = max(grades.values())
                for n in range(1,6):
                    print(str(n), round(70 * float(grades[n]) / m) * "*", "(" + str(grades[n]) + ")")
            movies = self.movies(member, grades)
            print("Got grades and info for %s movies" % len(movies))

            print("Getting IMDB links")
            for k,m in enumerate(movies):
                imdb = self.imdb(m['url'])
                print("\r" + str(int(100.0*((k+1)/len(movies)))) + "%", end='')
                sys.stdout.flush()
                if imdb:
                    m['imdb'] = imdb
                    #print("%s has IMDB id %s" % (m['o_title'], imdb))
            print()
    
            print("Reading comments")
            comments = self.comments(member)
            print("Found %s comments" % len(comments))
    
            # merge comments with movies
            for m in movies:
                comment_list = list(map(lambda y: (y[1], y[2]),
                                        filter(lambda x: x[0] == m['url'], 
                                               comments)))
                if comment_list:
                    m['comments'] = comment_list
            return movies

def main_filmtipset():
    b = FilmtipsetBrowser()
    #b.debug = True
    print("Username:", end=" ")
    sys.stdout.flush()
    user = sys.stdin.readline().strip()
    password = getpass.getpass()

    try:
        movies = b.load(user, password)
    except FilmtipsetLoginError:
        print("Wrong username or password")
        return

    f = open('./filmtipset-data.txt', 'w')
    f.write(str(movies))
    f.close()
    # for m in movies:
    #     print()
    #     print("%s - %s" % (m['title'], m['grade']))
    #     if 'comments' in m:
    #         for c in m['comments']:
    #             print("\t%s" % c[1])
    #             for l in c[0].splitlines():
    #                 print("\t%s" % l)

    # print(list(filter(lambda x: x['url'] == 'wargames-the-dead-code', movies))[0])

    # for m in movies: print(str(m))

if __name__ == "__main__":
    main_filmtipset()
