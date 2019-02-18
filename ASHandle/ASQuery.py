#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 11:13:28 2019

@author: s1881079
"""

#import SpaElem
import random

__all__ = ['findStptFromTrs','findTsFromStpt','findTrsFromTrs','findAdjZone','calLengthOfPath','getRiskinDist']

'''
def connect_dbs():

    try:
        conn = cx_Oracle.connect("s1889111/Muffle67@geosgen")
    except:
        print('Cannot link to database')
        return None

    return conn
'''

def findStptFromTrs(conn,cur_trsid):
    '''
    find start points from treasure point

    Parameters
    ----------
    conn : cx_oracle.conn
        database connect
    cur_trsid : int
        current treasure id

    Return
    ------
    list
        list containning the id of start point

    '''
    qy_expr = '''
    SELECT UNIQUE A.POINT_ID, B.PATH_ID, SDO_GEOM.SDO_LENGTH(B.GEOM, m.diminfo)
FROM s1889111.POINTS A, s1889111.PATHS B, s1889111.POINTS C, user_sdo_geom_metadata m
WHERE(B.START_POINT_ID = A.POINT_ID
AND B.END_POINT_ID = C.POINT_ID
AND C.POINT_ID = '{cr_trs}'
AND C.CLASS_ID = 1
AND A.CLASS_ID = 0)
OR
(B.END_POINT_ID = A.POINT_ID
AND B.START_POINT_ID = C.POINT_ID
AND C.POINT_ID = '{cr_trs}'
AND A.CLASS_ID =0
AND C.CLASS_ID = 1)
    '''.format(cr_trs = cur_trsid)
    cs = conn.cursor()
    cs.execute(qy_expr)
    list_linkedStptID = []
    list_linkedLinkID = []
    list_linkedLenth = []
    for row in cs:
        list_linkedStptID.append(row[0])
        list_linkedLinkID.append(row[1])
        list_linkedLenth.append(row[2])
    #return list_linkedStptID,list_linkedLinkID
    return list_linkedStptID,list_linkedLinkID,list_linkedLenth


def findTsFromStpt(conn,cur_stptid):
    '''
    find treasure points from start point

    Parameters
    ----------
    conn : cx_oracle.conn
        database connect
    cur_trsid : int
        current start point id

    Return
    ------
    list
        list containning the id of treasure points

    '''
    qy_expr = '''
    SELECT UNIQUE A.POINT_ID, B.PATH_ID, SDO_GEOM.SDO_LENGTH(B.GEOM, m.diminfo)
FROM s1889111.POINTS A, s1889111.PATHS B, s1889111.POINTS C, user_sdo_geom_metadata m
WHERE(B.START_POINT_ID = A.POINT_ID
AND B.END_POINT_ID = C.POINT_ID
AND C.POINT_ID = '{cr_stpt}'
AND C.CLASS_ID = 0
AND A.CLASS_ID = 1)
OR
(B.END_POINT_ID = A.POINT_ID
AND B.START_POINT_ID = C.POINT_ID
AND C.POINT_ID = '{cr_stpt}'
AND A.CLASS_ID = 1
AND C.CLASS_ID = 0)
    '''.format(cr_stpt = cur_stptid)
    cs = conn.cursor()
    cs.execute(qy_expr)
    list_linkedTrsID = []
    list_linkedLinkID = []
    list_linkedLenth = []
    for row in cs:
        list_linkedTrsID.append(row[0])
        list_linkedLinkID.append(row[1])
        list_linkedLenth.append(row[2])
    #return list_linkedTrsID,list_linkedLinkID
    return list_linkedTrsID,list_linkedLinkID,list_linkedLenth

def findTrsFromTrs(conn,cur_trsid,prev_trsid = []):
    '''
    find start points from treasure point

    Parameters
    ----------
    conn : cx_oracle.conn
        database connect
    cur_trsid : int
        current treasure id

    Return
    ------
    list
        list containning the id of start point

    '''
    qy_expr = '''
    SELECT UNIQUE A.POINT_ID, B.PATH_ID, SDO_GEOM.SDO_LENGTH(B.GEOM, m.diminfo)
FROM s1889111.POINTS A, s1889111.PATHS B, s1889111.POINTS C, user_sdo_geom_metadata m
WHERE(B.START_POINT_ID = A.POINT_ID
AND B.END_POINT_ID = C.POINT_ID
AND C.POINT_ID = '{cr_trs}'
AND C.CLASS_ID = 1
AND A.CLASS_ID = 1)
OR
(B.END_POINT_ID = A.POINT_ID
AND B.START_POINT_ID = C.POINT_ID
AND C.POINT_ID = '{cr_trs}'
AND A.CLASS_ID = 1
AND C.CLASS_ID = 1)
    '''.format(cr_trs = cur_trsid)
    exp_pxpr = " AND A.POINT_ID <> {prev}"

    for pid in prev_trsid:
        qy_expr = qy_expr + exp_pxpr.format(prev = pid)

    cs = conn.cursor()
    cs.execute(qy_expr)
    list_linkedTrsID = []
    list_linkedLinkID = []
    list_linkedLenth = []
    for row in cs:
        list_linkedTrsID.append(row[0])
        list_linkedLinkID.append(row[1])
        list_linkedLenth.append(row[2])
    #return list_linkedStptID,list_linkedLinkID
    return list_linkedTrsID,list_linkedLinkID,list_linkedLenth



def findAdjZone(conn,cur_zoneid):
    '''
    find adjacent zones

    Parameters
    ----------
    conn : cx_oracle.conn
        database connected
    cur_zoneid : int
        current zone id

    Return
    ------
    list
        list containing id of the adjacent zones

    '''
    qy_expr = '''
    select i.ADJZONE
  from (select /*+ORDERED*/
               A.ZONE_ID as ZONE,
               B.ZONE_ID as ADJZONE,
               sdo_geom.sdo_intersection(B.GEOM,A.GEOM,0.005) as geom
          from s1889111.ZONE A,
               s1889111.ZONE B
         where A.ZONE_ID = '{cr_zone}'
           and SDO_TOUCH(A.GEOM, B.GEOM) = 'TRUE'
       ) i
 where i.geom.sdo_gtype <> 2001
    '''.format(cr_zone = cur_zoneid)
    cs = conn.cursor()
    cs.execute(qy_expr)
    list_adjZoneID = []
    for row in cs:
        list_adjZoneID.append(row[0])

    return list_adjZoneID

def calLengthOfPath(conn,path_id):
    '''
    calculate the length of path specified by path_id

    Parameters
    ----------
    conn : cx_oracel,conn
        database connected
    path_id : int
        id of path to calculate

    Return
    ------
    float
        length of the targetted path

    '''
    qy_expr = '''
    SELECT SDO_GEOM.SDO_LENGTH(c.geom, m.diminfo)
FROM s1889111.paths c, user_sdo_geom_metadata m
WHERE m.table_name = 'PATHS'
AND c.path_id = '{qy_path}'
AND m.column_name = 'GEOM'
    '''.format(qy_path = path_id)
    cs = conn.cursor()
    cs.execute(qy_expr)
    for row in cs:
        path_length = row[0]
    return path_length

def defRiskStatus(penalty,distance):
    '''
    risk staus is defined by both penalty and the distance
    between road and risks. the further the risk is ,the larger
    the possibiliity that this risk would sleepself.
    once triggered, would cause death or add distance
    '''

    sleepFactor = distance / 100
    rand = random.random()
    if rand > sleepFactor:
        if penalty == 3:
            return 3,0
        elif penalty == 2:
            return 2,500
        else:
            return 1,100
    else:
        return 0,0


def getRiskinDist(conn,path_id):
    '''

    '''
    qy_expr = '''
    SELECT i.RISK_ID, i.PENALTY_ID, i.GEOM AS Distance
    FROM (SELECT /*ORDERED*/
      A.PATH_ID, B.RISK_ID, B.PENALTY_ID,
    SDO_GEOM.SDO_DISTANCE(A.GEOM, B.GEOM, 0.005) AS GEOM
    FROM s1889111.PATHS A, s1889111.RISKS B
    WHERE A.PATH_ID = '{qy_path}') i
    WHERE i.GEOM < 100
    '''.format(qy_path = path_id)
    cs = conn.cursor()
    cs.execute(qy_expr)
    list_riskid = []
    list_status = []
    list_adddis = []
    list_disToRoad = []
    for row in cs:
        riskid,penalty,distance = (row[0],row[1],row[2])
        list_riskid.append(riskid)
        status,adddis = defRiskStatus(penalty,distance)
        list_status.append(status)
        list_adddis.append(adddis)
        list_disToRoad.append(distance)

    return list_riskid,list_status,list_adddis,list_disToRoad



'''
if __name__ == '__main__':
    conn = playground.connect_dbs()
    adZone1 = findAdjZone(conn,1)
    linktrs1 = findTsFromStpt(conn,1)
    linkstpt8 = findStptFromTrs(conn,8)
    p1_length = calLengthOfPath(conn,1)
    '''
