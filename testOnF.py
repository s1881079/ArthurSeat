#!/usr/bin/env python3
import json
import cgi
import cgitb
import ASHandle as ash
cgitb.enable()


if __name__ == '__main__':
    conn = ash.connect_dbs()
    indata = cgi.FieldStorage()
    #indata = {'key':'get_stpt_from_tres','tres_id':'5'}
    print('Content-Type: text/html\n')

    #test_str = '''
    if indata['key'].value == 'get_tres_from_stpt':
        #get treasur from startpoint
        cur_stptid = indata['stpt_id'].value
        list_tres,list_links,list_length = ash.findTsFromStpt(conn,cur_stptid)
        json_tres = json.dumps({'l_trs' : list_tres,'l_link' : list_links,'l_lengths' : list_length})


        print(json_tres)
    if indata['key'].value == 'get_tres_from_tres':
        #get tresure from treasure
        cur_treaid = indata['tres_id'].value
        prev_ptid = []
        #when comming across tje first treasure, there's no former treasure
        try:
            str_prev_ptid = indata['previd'].value.split(',')
            for i in str_prev_ptid:
                prev_ptid.append(int(i))
        except:
            pass
        list_tres,list_links,list_length = ash.findTrsFromTrs(conn,cur_treaid,prev_ptid)
        json_tres = json.dumps({'l_trs' : list_tres,'l_link' : list_links,'l_lengths' : list_length})
        print(json_tres)

    if indata['key'].value == 'get_adj_zone':
        #get adjacent zone
        cur_zoneid = indata['zone_id'].value
        list_adjzone = ash.findAdjZone(conn,cur_zoneid)
        json_zones = json.dumps({'l_adjz' : list_adjzone})

        print(json_zones)

    if indata['key'].value == 'get_info_of_risk':
        cur_pathid = indata['link_id'].value
        list_riskid,list_status,list_adddis,list_disToRoad = ash.getRiskinDist(conn,cur_pathid)
        json_risks = json.dumps({'l_riskid' : list_riskid,'l_risksta' : list_status,'l_adddis' : list_adddis,'l_todis' : list_disToRoad})

        print(json_risks)

    if indata['key'].value == 'get_stpt_from_tres':
        #get treasur from startpoint
        cur_tresid = indata['tres_id'].value
        list_stpt,list_links,list_length = ash.findStptFromTrs(conn,cur_tresid)
        json_stpt = json.dumps({'l_stpt' : list_stpt,'l_link' : list_links,'l_lengths' : list_length})


        print(json_stpt)
