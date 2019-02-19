#!/usr/bin/env python3

import cgi
import cgitb
import ASHandle as ash
from jinja2 import Environment, FileSystemLoader
cgitb.enable()



if __name__ == '__main__':
    conn = ash.connect_dbs()
    #grab all information for display
    start_pt_geojson = ash.getInfoFromDB(conn,'get_start_pts')
    zones_geojson = ash.getInfoFromDB(conn,'get_zone_polygons_pts')
    treasure_geojson = ash.getInfoFromDB(conn,'get_treasure_pts')
    risk_geojson = ash.getInfoFromDB(conn,'get_risk_pts')
    link_geojson = ash.getInfoFromDB(conn,'get_link_pts')

#JINJA
    env = Environment(loader = FileSystemLoader('templates'))
    template = env.get_template('game.html')

    print('Content-Type: text/html\n')
    print(template.render(
        zones_json = zones_geojson,
        stpts_json = start_pt_geojson,
        treasures_json = treasure_geojson,
        risks_json = risk_geojson,
        links_json = link_geojson
    ))
