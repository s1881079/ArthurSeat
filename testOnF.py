#!/usr/bin/env python3
import json
import cgi
import cgitb
import ASHandle as ash
cgitb.enable()


if __name__ == '__main__':
    conn = ash.connect_dbs()

    indata = cgi.FieldStorage()
    #indata = {'key' : 'get_info_of_risk', 'link_id' : 8}
    print('Content-Type: text/html\n')
    #json_test = json.dumps({'res' : 'i am fine'});
    #print(json_test)
    #print(indata)
    #test_str ='''
    if indata['key'].value == 'get_tres_from_stpt':

        cur_stptid = indata['stpt_id'].value
        list_tres,list_links,list_length = ash.findTsFromStpt(conn,cur_stptid)
        json_tres = json.dumps({'l_trs' : list_tres,'l_link' : list_links,'l_lengths' : list_length})


        print(json_tres)
    if indata['key'].value == 'get_tres_from_tres':
        #print('i ama here')

        cur_treaid = indata['tres_id'].value
        prev_ptid = []
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
        cur_zoneid = indata['zone_id'].value
        list_adjzone = ash.findAdjZone(conn,cur_zoneid)
        json_zones = json.dumps({'l_adjz' : list_adjzone})

        print(json_zones)

    if indata['key'].value == 'get_info_of_risk':
        cur_pathid = indata['link_id'].value
        list_riskid,list_status,list_adddis,list_disToRoad = ash.getRiskinDist(conn,cur_pathid)
        json_risks = json.dumps({'l_riskid' : list_riskid,'l_risksta' : list_status,'l_adddis' : list_adddis,'l_todis' : list_disToRoad})

        print(json_risks)
