prompt identidad de sesion
select 'session_user=' || sys_context('userenv', 'session_user') || '|current_schema=' || sys_context('userenv', 'current_schema')
from dual;

prompt privilegios efectivos de sistema
select 'system_privilege=' || privilege
from session_privs
order by privilege;

prompt roles efectivos de sesion
select 'role=' || role
from session_roles
order by role;

prompt privilegios de objeto relevantes
select 'object_privilege=' || owner || '.' || table_name || ':' || privilege
from user_tab_privs
where owner in ('DATA', 'APEX_240100')
order by owner, table_name, privilege;
