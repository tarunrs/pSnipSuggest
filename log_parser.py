from sqlparser import sql_parse

t = sql_parse("SELECT p.objID,str(p.ra,13,8) as ra,str(p.dec,13,8) as dec,p.u,p.err_u,p.g,p.err_g,p.r,p.err_r,p.i,p.err_i,p.z,p.err_z,p.type,isnul(s.mjd,0) as mjd,ISNULL(s.z,0) as z,ISNULL(s.zErr,0) as zErr,ISNULL(s.zConf,0) as zConf,ISNULL(s.zWarning,0) as zWarning,ISNULL(s.specClass,0) as specClass FROM dbo.fGetNearbyObjEq(322.336871, 11.493331,10) as b, BESTDR5..PhotoObj as p LEFT OUTER JOIN BESTDR5..SpecObj s ON p.objID = s.bestObjID WHERE b.objID = p.objID")
print "table \n\n", t.tables[0].table_function
print "columns \n\n", t.tables[1]


