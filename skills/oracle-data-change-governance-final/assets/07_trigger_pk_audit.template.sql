/*
	object: data.tr_<table_name>_biu
	purpose: assign identifier and mandatory audit values
	owner: data
	dependencies: data.pk_commons, data.<table_name>
	deployment: <change-id>, step 07
	validation: insert approved TEST data and verify identifier/audit values
	rollback: drop trigger data.tr_<table_name>_biu
*/
create or replace trigger data.tr_<table_name>_biu
	before insert or update on data.<table_name>
	for each row
begin
	if inserting and :new.id is null then
		data.pk_commons.sp_secuencia('data.<table_name>', :new.id);
	end if;

	if inserting then
		:new.usercrea := nvl(v('user'), 'ORCL');
		:new.fechcrea := systimestamp;
	end if;

	:new.usermodi := nvl(v('user'), 'ORCL');
	:new.fechmodi := systimestamp;
end;
/

commit;
