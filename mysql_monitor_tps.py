#!/usr/bin/env python
#coding=utf-8
from optparse import OptionParser
import time
import sys
import os
import MySQLdb
head1="[-------------------------------------------------->>"
head2="<<--------------------------------------------------]"

def get_cli_options():
    parser = OptionParser(usage="usage: python %prog [options]",
                          description="""This script prints MySQL TPS QPS""")

    parser.add_option("-H", "--host",
                      dest="host",
                      default="localhost",
                      metavar="HOST",
                      help="mysql host")
    parser.add_option("-P", "--port",
                      dest="port",
                      default=3306,
                      metavar="PORT",
                      help="mysql port")
    
    parser.add_option("-I", "--interval",
                      dest="interval",
                      default=1,
                      metavar="interval",
                      help="default 1")
    (options, args) = parser.parse_args()

    return options


def main() :
    options = get_cli_options()
    try: 
      conn = MySQLdb.connect(host=options.host,port=int(options.port),user='username',passwd='passwd', charset='utf8')
    except  MySQLdb.Error,e:
      print "Error %d:%s"%(e.args[0],e.args[1])
      exit(1)
    cursor=conn.cursor()
    conn.autocommit(True)
    count=1
    mystat1={}
    mystat2={}
    sql = "show global status where Variable_name in ('Com_commit','Com_delete','Com_insert','Com_select','Com_update',\
                                                      'Innodb_buffer_pool_read_requests','Innodb_buffer_pool_reads','Threads_running',\
                                                      'Threads_connected','Threads_cached','Threads_created');"
    print head1,options.host,options.port,head2
    while True:
       try :
          cursor.execute(sql)
          results1 = cursor.fetchall()
          mystat1=dict(results1)
          diff =int(options.interval) 
          time.sleep(diff)
          cursor.execute(sql)
          results2 = cursor.fetchall()
          mystat2=dict(results2)

          Com_diff = (int(mystat2['Com_commit'])   - int(mystat1['Com_commit']) ) / diff 
          del_diff = (int(mystat2['Com_delete'])   - int(mystat1['Com_delete']) ) / diff
          ins_diff = (int(mystat2['Com_insert'])   - int(mystat1['Com_insert']) ) / diff
          sel_diff = (int(mystat2['Com_select'])   - int(mystat1['Com_select']) ) / diff
          upd_diff = (int(mystat2['Com_update'])   - int(mystat1['Com_update']) ) / diff
          hit_diff = float(mystat2['Innodb_buffer_pool_read_requests'])-float(mystat2['Innodb_buffer_pool_reads'])
          hit_buff =hit_diff/float(mystat2['Innodb_buffer_pool_read_requests'])*100
          thr_run  = int(mystat2['Threads_running'])
          thr_cre  = int(mystat2['Threads_created'])-int(mystat1['Threads_created']) 
          thr_crc  = int(mystat2['Threads_cached'])
          thr_con  = int(mystat2['Threads_connected'])
          qps_s=sel_diff
          tps_iud = del_diff+ins_diff+upd_diff
          dt=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) 
          count=count+1
          print 'sel:%-5s ins:%-5s upd:%-5s del:%-5s iud:%-5s cre:%-4s run:%-4s con:%-4s cac:%-4s hit~%4.2f time=%14s' \
                %(qps_s,ins_diff,upd_diff,del_diff,tps_iud,thr_cre,thr_run,thr_con,thr_crc,hit_buff,dt)
          if count%30==0:
              print head1,hostname,myport,head2
          else:
             "ok"
       except KeyboardInterrupt :
          print "exit .."
          sys.exit()
  
    conn.close()
if __name__ == '__main__':
   main()