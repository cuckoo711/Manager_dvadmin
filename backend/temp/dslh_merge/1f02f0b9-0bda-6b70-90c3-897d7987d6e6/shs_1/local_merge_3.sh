#!/bin/bash
SOCDATABASE=ycneg01xyxms10
DESTDATABASE=ycneg01xyxms9
DESTSERVERID=101
DB_USER=root
DB_IP=127.0.0.1
DB_PASS="DhdKYRhBCte16YSX"
DB_PORT=33008
BACKUP=/home/merge/merge
mkdir -p "/home/merge/merge1"
MERGE=/home/merge/merge1

export MYSQL_PWD=$DB_PASS

#创建并导入新的两个数据库进行合并
SOUTEMPDATABASE=tempsousanguo
DESTTEMPDATABASE=tempdestsanguo
create_socdb_sql="create database IF NOT EXISTS ${SOUTEMPDATABASE} default character set utf8mb4 COLLATE utf8mb4_bin;"
create_destdb_sql="create database IF NOT EXISTS ${DESTTEMPDATABASE} default character set utf8mb4 COLLATE utf8mb4_bin;"

mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${create_socdb_sql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${create_destdb_sql}"
echo "创建临时数据库完成"

mysql -u$DB_USER -h $DB_IP -P$DB_PORT  ${SOUTEMPDATABASE} < ${BACKUP}\/${SOCDATABASE}.sql
echo "导入源数据完成"
#联表删除死人数据
delete_sousql="DELETE a,b,c,d FROM players a LEFT JOIN roles b ON a.dbid = b.playerid LEFT JOIN mails c ON a.dbid = c.playerid LEFT JOIN items d ON a.dbid = d.playerid where (a.recharge=0 AND a.level<40) OR (a.lastonlinetime<(unix_timestamp()-7*24*60*60) AND a.recharge=0 and a.level<150);"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${SOUTEMPDATABASE} -e "${delete_sousql}"
echo "源数据库死人数据清理完毕"


mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} < ${BACKUP}\/${DESTDATABASE}.sql
echo "导入目标数据完成"
delete_destsql="DELETE a,b,c,d FROM players a LEFT JOIN roles b ON a.dbid = b.playerid LEFT JOIN mails c ON a.dbid = c.playerid LEFT JOIN items d ON a.dbid = d.playerid where (a.recharge=0 AND a.level<40) OR (a.lastonlinetime<(unix_timestamp()-7*24*60*60) AND a.recharge=0 and a.level<150);"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${delete_destsql}"
echo "目标数据库死人数据清理完毕"

#处理账号重复问题
update_accountsql="UPDATE ${DESTTEMPDATABASE}.players as a, ${SOUTEMPDATABASE}.players as b SET a.account=CONCAT(a.account,a.serverid),b.account=CONCAT(b.account,b.serverid);"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${update_accountsql}"
echo "players账号重名处理完成"

#处理players重名问题 处理guild重名问题
update_playersql="UPDATE ${DESTTEMPDATABASE}.players as a, ${SOUTEMPDATABASE}.players as b SET b.name=CONCAT(b.name,b.serverid) where b.name=a.name;"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${update_playersql}"
echo "players重名处理完成"

update_guildsql="UPDATE ${DESTTEMPDATABASE}.guild as a, ${SOUTEMPDATABASE}.guild as b SET b.name=CONCAT(b.name,b.serverid) where b.name=a.name;"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${update_guildsql}"
echo "公会重名处理完成"

#合并players,roles,mails,guild,items,rechargerecord
merge_playsql="INSERT INTO ${DESTTEMPDATABASE}.players SELECT * FROM ${SOUTEMPDATABASE}.players;"
merge_rolesql="INSERT INTO ${DESTTEMPDATABASE}.roles(playerid,totalpower,skill,ride_data,wing_data,fairy_data,weapon_data,equips_data,title_data,skin_data,vein_data,panacea_data,spells_res,fly_data) SELECT playerid,totalpower,skill,ride_data,wing_data,fairy_data,weapon_data,equips_data,title_data,skin_data,vein_data,panacea_data,spells_res,fly_data FROM ${SOUTEMPDATABASE}.roles;"
merge_mailssql="INSERT INTO ${DESTTEMPDATABASE}.mails(playerid,readstatus,sendtime,head,context,award,awardstatus,log_type,log) SELECT playerid,readstatus,sendtime,head,context,award,awardstatus,log_type,log FROM ${SOUTEMPDATABASE}.mails;"
merge_guildsql="INSERT INTO ${DESTTEMPDATABASE}.guild SELECT * FROM ${SOUTEMPDATABASE}.guild;"
merge_itemssql="INSERT INTO ${DESTTEMPDATABASE}.items(playerid,bag_type,id,count,attrs,invalidtime) SELECT playerid,bag_type,id,count,attrs,invalidtime FROM ${SOUTEMPDATABASE}.items;"
merge_rechargerecordsql="INSERT INTO ${DESTTEMPDATABASE}.rechargerecord(orderid,amount,paytime,gameorder,channel,channel_uid,serverid,playerid,goodsid) SELECT orderid,amount,paytime,gameorder,channel,channel_uid,serverid,playerid,goodsid FROM ${SOUTEMPDATABASE}.rechargerecord;"

mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${merge_playsql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${merge_rolesql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${merge_mailssql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${merge_guildsql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${merge_itemssql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${merge_rechargerecordsql}"
echo "数据合并完成"

#清空不必要表数据
clear_arenasql="truncate table arena;"
clear_activityssql="truncate table activitys;"
clear_logsql="truncate table log;"
clear_auctionssql="truncate table auctions;"
clear_rankssql="truncate table ranks;"
clear_gmcmdsql="truncate table gmcmd;"
clear_paysql="truncate table pay;"
clear_wardatassql="truncate table wardatas;"
clear_worlddatassql="truncate table worlddatas;"
clear_recordssql="truncate table records;"
clear_qpsql="truncate table qualifying_player;"
clear_qrsql="truncate table qualifying_record;"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_arenasql}"
#mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_activityssql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_logsql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_auctionssql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_rankssql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_gmcmdsql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_paysql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_wardatassql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_worlddatassql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_recordssql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_qpsql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${clear_qrsql}"
echo "数据表清理完成"

#修改players,guild里面的serverid
up_pserveridsql="UPDATE players SET serverid=${DESTSERVERID} WHERE serverid!=${DESTSERVERID};"
up_gserveridsql="UPDATE guild SET serverid=${DESTSERVERID} WHERE serverid!=${DESTSERVERID};"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${up_pserveridsql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT ${DESTTEMPDATABASE} -e "${up_gserveridsql}"
echo "更新serverid完成"

#导出合并后的数据库数据
mysqldump -u$DB_USER -h $DB_IP -P$DB_PORT -R --opt $DESTTEMPDATABASE > ${MERGE}\/${DESTDATABASE}.sql

#删除临时创建的数据库跟已经被合并的数据库
drop_tmpsousql="drop database ${SOUTEMPDATABASE};"
drop_tmpdestsql="drop database ${DESTTEMPDATABASE}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${drop_tmpsousql}"
mysql -u$DB_USER -h $DB_IP -P$DB_PORT -e "${drop_tmpdestsql}"
echo "删除合并数据库完成"