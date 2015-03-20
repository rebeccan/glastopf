# Copyright (C) 2015  Rebecca Neigert
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import os
import os.path
from glastopf.modules.events import attack
from sqlalchemy import create_engine
from datetime import datetime
from datetime import timedelta


class Event(object):
    def __init__(self, identifier, time, source, request_url, request_raw, pattern):
        self.id = int(identifier)
        self.time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        cutPort = source.find(":")
        if(cutPort == -1 ):
            self.source = source
        else:
            self.source = source[:cutPort]
        self.request_raw = request_raw
        self.request_url = request_url
        self.pattern = pattern
       
        

class WebAnalyzer(object):
    
    def __init__(self, dbfile):
        self.events = []
        engine = create_engine('sqlite:///db/realAttackers.db')
        connection = engine.connect()
        trans = connection.begin()
        result = connection.execute("SELECT * FROM events WHERE pattern != 'style_css' order by source, events.time ASC")
        for row in result:
            self.events.append(Event(row['id'], row['time'], row['source'], row['request_url'], row['request_raw'], row['pattern']))
        trans.commit()
        connection.close()
    
    
    
    def sublistHuman(self):
        eventsHuman = []
        for e in self.events:
            if(not 'Googlebot' in e.request_raw and not 'Baiduspider' in e.request_raw):
                eventsHuman.append(e)
        return eventsHuman   
        
    
    def sublistVisits(self):
        visits = []
        eventsHuman = self.sublistHuman()
        visit = []
        previousEvent = None
        for event in eventsHuman:
            if(previousEvent is not None):
                if(not (previousEvent.source == event.source)):
                    visits.append(visit)
                    visit = []
                elif(event.time - previousEvent.time > timedelta(minutes=30)):
                    visits.append(visit)
                    visit = []
                    
            visit.append(event)
            previousEvent = event 
            
        return visits
    
    def time_visit(self, visit):
        length = timedelta()
        previousEvent = None
        for event in visit:
            if(previousEvent is not None):
                delta = event.time - previousEvent.time
                length = length + delta
            previousEvent = event 
        return length
    
    
    """the number of page views (page impressions) of a web page accessed by a human visitor (without crawlers/spiders/robots)"""
    def metric_pageViews(self):
        return len(self.sublistHuman())

    def metric_pageViewsWithCrawlers(self):
        return len(self.events)
    
    """sequence of page views of a unique visitor without interruption (of usually 30 minutes)"""
    def metric_visits(self):
        return len(self.sublistVisits())
    
    """the number of unique visitors (users) on a website"""
    def metric_visitors(self):
        eventsHuman = self.sublistHuman()
        count = 0
        previousEvent = None
        for event in eventsHuman:
            if(previousEvent is not None):
                if(not (previousEvent.source == event.source)):
                    count = count + 1
            previousEvent = event
        return count + 1
    
    """the avg number of page views during a visit for all visitors"""
    def metric_avgPagesPerVisit(self):
        pageViews = float(self.metric_pageViews())
        visits = float(self.metric_visits())
        return pageViews/visits
        
    """the avg length of time for all visitors spent on the website
    here: calculated avg time on site per visitor, not per visit""" 
    def metric_timeOnSite(self):
        visits = self.sublistVisits()
        length = timedelta()
        for visit in visits:
            length = length + self.time_visit(visit)
        visitors = self.metric_visitors()
        return length / visitors
    
    """the capability of a web page to keep a visitor on the website"""
    def metric_stickiness(self):
        pass
    
    """the percentage of single page view visits"""
    def metric_bounceRate(self):
        #find single page view visits
        visits = self.sublistVisits()
        singleCount = 0
        for visit in visits:
            if(len(visit) == 1):
                singleCount = singleCount + 1
        percentage = float(singleCount) / float(len(visits))
        return percentage
        
    """the number of visits, a visitor made on the site (=loyalty)"""
    def metric_frequency(self):
        visits = self.sublistVisits()
        minimum = sys.maxint
        maximum = 0
        previousSource = None
        countVisitsPerVisitor = 1
        for visit in visits:
            source = visit[0].source
            if(previousSource is not None):
                if(not previousSource == source):
                    minimum = min(minimum, countVisitsPerVisitor)
                    maximum = max(maximum, countVisitsPerVisitor)
                    countVisitsPerVisitor = 1
                else: countVisitsPerVisitor = countVisitsPerVisitor + 1
                
            previousSource = source 
        
        average = float(len(visits)) / float(self.metric_visitors())
        return minimum, maximum, average
        

def main():
    
    wa = WebAnalyzer('sqlite:///db/realAttackers.db')
    
    print "Events (=page views with crawlers): " + str(wa.metric_pageViewsWithCrawlers())
    print "Page Views: " + str(wa.metric_pageViews())
    
    print "Visits: " + str(wa.metric_visits())
    print "Visitors: " + str(wa.metric_visitors())
    
    print "Average page views per visit: " + str(wa.metric_avgPagesPerVisit())
    print "Time on Site: " + str(wa.metric_timeOnSite())
    
    print "Stickiness: " + str(wa.metric_stickiness())
    print "Bounce rate: " + str(wa.metric_bounceRate())
    
    minimum, maximum, average = wa.metric_frequency()
    print "Frequency: min: " + str(minimum) + " max: " + str(maximum) + " average: " + str(average)
    
    #\item \textbf{Page Views} is "the number of page views (page impressions) of a web page accessed by a human visitor (without crawlers/spiders/robots)" \cite{fasel2009fuzzy}.
    #The page, that is generated by the SQLInjectableEmulator, which is the default emulator now, has ... visits of probable real attackers.
    #%SELECT COUNT(*) FROM events where (request_raw not like '%Googlebot%' or '%Baiduspider%') and (pattern = 'sqlinjectable') = 2392
    #%all pages
    #%SELECT COUNT(*) FROM events where (request_raw not like '%Googlebot%' or '%Baiduspider%') = 4357
    #%SELECT COUNT(*) FROM events = 10216


if __name__ == "__main__":
    sys.exit(main())