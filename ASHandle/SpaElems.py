#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 14:27:36 2019

@author: s1881079
"""
import numpy as np
import cx_Oracle
import pandas as pd
import json
import pyproj
#from jinja2 import Environment, FileSystemLoader


class Point:
    def __init__(self,r_x,r_y):
        self.x = r_x
        self.y = r_y

    def toLatLon(self):
        wgs84=pyproj.Proj("+init=EPSG:4326")
        map_proj = pyproj.Proj("+init=EPSG:3857")
        lon,lat = pyproj.transform(map_proj,wgs84, self.x, self.y)
        self.x = lon
        self.y = lat

    def getLatLon(self):
        self.toLatLon()
        return [self.x,self.y]

    def coorToGeoJson(self):
        return {'type' : 'Point',
                'coordinates':[self.x,self.y]}


class StartPoint(Point):
    def __init__(self,iterable):
        r_id,r_zone,r_x,r_y = iterable
        self.id = r_id
        self.zone = r_zone
        self.x = r_x
        self.y = r_y

    def toGeoJson(self):
        return {'type' : 'Feature',
                'properties' : {
                        'start_id' : self.id,
                        'zone_id' : self.zone
                        },
                'geometry':self.coorToGeoJson()}


class TreasurePoint(Point):
    def __init__(self,iterable):
        #print(len(iterable))
        r_id,r_zone,r_x,r_y = iterable
        self.id = r_id
        self.x = r_x
        self.y = r_y
        self.zone = r_zone

    def toGeoJson(self):
        return {'type' : 'Feature',
                'properties' : {
                        'treasure_id' : self.id,
                        'zone_id' : self.zone
                        },
                'geometry':self.coorToGeoJson()}

class RiskPoint(Point):
    def __init__(self,iterable):
        r_id,r_x,r_y,r_zone,r_penalty = iterable
        self.id = r_id
        self.x = r_x
        self.y = r_y
        self.zone = r_zone
        self.penalty = r_penalty

    def toGeoJson(self):
        return {'type' : 'Feature',
                'properties' : {
                        'risk_id' : self.id,
                        'zone_id' : self.zone,
                        'penalty_id' : self.penalty
                        },
                'geometry':self.coorToGeoJson()}

class PointSeqs(list):
    def __init__(self,ar_x=[],ar_y=[]):
        c_point = len(ar_x)
        for i in range(c_point):
            self.append(Point(i,ar_x[i],ar_y[i]))

    def coorArrToGeoJson(self):
        coor_list = []
        for pt in self:
            coor_list.append(pt.getLatLon())
        return coor_list

class LinkLineString(PointSeqs):
    def __init__(self,r_id,r_stpt,r_edpt,ar_x=[],ar_y=[]):
        self.id = r_id
        self.st_pt = r_stpt
        self.ed_pt = r_edpt
        c_point = len(ar_x)
        for i in range(c_point):
            self.append(Point(ar_x[i],ar_y[i]))

    def toGeoJson(self):
        return {'type' : 'Feature',
                'properties' : {
                        'link_id' : self.id,
                        'start_point' : str(self.st_pt),
                        'end_point' : str(self.ed_pt)
                        },
                'geometry':{
                        'type' : 'LineString',
                        'coordinates' : self.coorArrToGeoJson()
                        }}

class ZonePolygon(PointSeqs):

    def __init__(self,zone_id,ar_x=[],ar_y=[]):
        self.id = zone_id
        c_point = len(ar_x)
        for i in range(c_point):
            self.append(Point(ar_x[i],ar_y[i]))

    def toGeoJson(self):
        return {'type' : 'Feature',
                'properties' : {
                        'zone_id' : self.id
                        },
                'geometry':{
                        'type' : 'Polygon',
                        'coordinates' : [self.coorArrToGeoJson()]
                        }}


def connect_dbs():
    '''
    connect to database
    '''
    try:
        conn = cx_Oracle.connect("s1889111/Muffle67@geosgen")
    except:
        print('Cannot link to database')
        return None

    return conn


def grab_info(table_key):
    '''
    return sql plus command according to keyword
    '''
    qy_switcher = {
            'get_start_pts' : "select c.point_id,c.zone_id, t.x, t.y from s1889111.points c, table(sdo_util.getvertices(c.geom)) t where c.class_id = (select class_id from s1889111.point_class where type = 'START_POINT')",
            'get_zone_polygons_pts' : 'select c.zone_id, t.x, t.y from s1889111.zone c, table(sdo_util.getvertices(c.geom)) t',
            'get_treasure_pts' : "select c.point_id,c.zone_id, t.x, t.y from s1889111.points c, table(sdo_util.getvertices(c.geom)) t where c.class_id = (select class_id from s1889111.point_class where type = 'TREASURE_POINT')",
            'get_link_pts' : 'select c.path_id, c.start_point_id, c.end_point_id, t.x, t.y from paths c, table(sdo_util.getvertices(c.geom)) t',
            'get_risk_pts' : 'select c.risk_id, t.x, t.y, c.zone_id, c.penalty_id from s1889111.risks c, table(sdo_util.getvertices(c.geom)) t'
    }

    return qy_switcher.get(table_key)


def getPtsJson(cs,table_key):
    '''
    generate GeoJson for startpoints
    '''
    points_json_list = []
    for pt in cs:
        if table_key == 'get_start_pts':
            obj_pt = StartPoint(pt)
        elif table_key == 'get_treasure_pts':
            obj_pt = TreasurePoint(pt)
        elif table_key == 'get_risk_pts':
            obj_pt = RiskPoint(pt)
        obj_pt.toLatLon()
        points_json_list.append(obj_pt.toGeoJson())

    return json.dumps(points_json_list)

def getLinkLineJson(cs):
    '''
    generate GeoJson for zones
    '''
    list_rec = []
    for row in cs:
        list_rec.append([i for i in row])

    df = pd.DataFrame(list_rec, columns = ['link_id','st_pt','ed_pt','x','y'])
    xs_list = []
    ys_list = []
    stpt_list = []
    edpt_list = []
    linkid_list = []
    for link_id, pt in df.groupby('link_id'):
        linkid_list.append(link_id)
        stpt_list.append(pt.st_pt)
        edpt_list.append(pt.ed_pt)
        xs_list.append(pt.x)
        ys_list.append(pt.y)

    links_json_list = []
    for i in range(len(linkid_list)):
        links_json_list.append(LinkLineString(linkid_list[i],np.array(stpt_list[i])[0],np.array(edpt_list[i])[0],np.array(xs_list[i]),np.array(ys_list[i])).toGeoJson())

    return json.dumps(links_json_list)

def getZonePolyJson(cs):
    '''
    generate GeoJson for zones
    '''
    list_rec = []
    for row in cs:
        list_rec.append([row[0],row[1],row[2]])

    df = pd.DataFrame(list_rec, columns = ['zone_id','x','y'])
    xs_list = []
    ys_list = []
    zoneid_list = []
    for zone_id, pt in df.groupby('zone_id'):
        zoneid_list.append(zone_id)
        xs_list.append(pt.x)
        ys_list.append(pt.y)

    zones_json_list = []
    for i in range(len(zoneid_list)):
        zones_json_list.append(ZonePolygon(zoneid_list[i],np.array(xs_list[i]),np.array(ys_list[i])).toGeoJson())

    return json.dumps(zones_json_list)


def formObjectJson(cs,table_key):
    '''
    return geoJson according to object type
    '''
    if table_key == 'get_start_pts' or table_key == 'get_treasure_pts' or table_key == 'get_risk_pts':
        rst_json = getPtsJson(cs,table_key)
    if table_key == 'get_zone_polygons_pts':
        rst_json = getZonePolyJson(cs)
    if table_key == 'get_link_pts':
        rst_json = getLinkLineJson(cs)

    return rst_json

def getInfoFromDB(conn,table_key):
    '''
    extract information from database
    '''
    qy_expr = grab_info(table_key)
    cs = conn.cursor()
    cs.execute(qy_expr)

    rst = formObjectJson(cs,table_key)

    return rst

if __name__ == '__main__':
    conn = connect_dbs()
    start_pt_geojson = getInfoFromDB(conn,'get_start_pts')
    zones_geojson = getInfoFromDB(conn,'get_zone_polygons_pts')
    treasure_geojson = getInfoFromDB(conn,'get_treasure_pts')
    risk_geojson = getInfoFromDB(conn,'get_risk_pts')
    link_geojson = getInfoFromDB(conn,'get_link_pts')

#JINJA
#    env = Environment(loader = FileSystemLoader('template'))
#    template = env.get_template('playground.html')
#    print('Content-Type: text/html\n')
#    print(template.render(
#        zones_json = zones_geojson,
#        stpts_json = start_pt_geojson
#    ))
