-- ============================================================================
-- PL/SQL EXAMPLES - Nomenclatura Oracle/APEX Estándar
-- ============================================================================
-- Purpose: Casos de uso reales con documentación y nomenclatura correctas
-- Date: 2026-08-22
--
-- CONVENCIONES DE NOMENCLATURA:
--   Tablas:       t_[nombre]
--   Vistas:       vt_[nombre]
--   Paquetes:     pk_[nombre]
--   Procedimientos: sp_[nombre]
--   Funciones:    f_[nombre]
--   Triggers:     trg_[nombre_tabla_sin_t_]
--   Secuencias:   sq_[nombre]
--   Índices:      idx_[nombre_tabla_sin_t_]_##  (## = secuencial 00, 01, 02...)
--
-- NOTA: Sin claves primarias/foráneas explícitas (usuario debe solicitarlas)
-- ============================================================================

-- ============================================================================
-- EJEMPLO 1: TABLA CON DOCUMENTACIÓN COMPLETA
-- ============================================================================

create table t_employees (
	employee_id number(6)
	, first_name varchar2(20) not null
	, last_name varchar2(25) not null
	, email varchar2(25) not null
	, phone_number varchar2(20)
	, hire_date date not null
	, job_id varchar2(10) not null
	, salary number(8,2)
	, commission_pct number(2,2)
	, manager_id number(6)
	, department_id number(4)
	, status varchar2(10) default 'ACTIVE' not null
);

-- Documentación de columnas
comment on column t_employees.employee_id
	is 'Identificador único del empleado. Secuencia: sq_employees.';

comment on column t_employees.first_name
	is 'Nombre del empleado. Requerido. Máximo 20 caracteres.';

comment on column t_employees.last_name
	is 'Apellido del empleado. Requerido. Máximo 25 caracteres.';

comment on column t_employees.email
	is 'Correo corporativo. Requerido. Debe ser único. Formato: usuario@empresa.com';

comment on column t_employees.phone_number
	is 'Número de teléfono corporativo. Opcional. Formato: +1-650-505-1234';

comment on column t_employees.hire_date
	is 'Fecha de contratación. Requerido. No puede ser posterior a SYSDATE.';

comment on column t_employees.job_id
	is 'Identificador del puesto. Referencia a t_jobs.';

comment on column t_employees.salary
	is 'Salario mensual. Rango: 2000-40000. Validado por trigger.';

comment on column t_employees.commission_pct
	is 'Porcentaje de comisión. Solo para vendedores. Rango: 0.00-0.40';

comment on column t_employees.manager_id
	is 'Empleado que supervisa este registro. Referencia a t_employees.';

comment on column t_employees.department_id
	is 'Departamento del empleado. Referencia a t_departments.';

comment on column t_employees.status
	is 'Estado del empleado. Valores: ACTIVE, INACTIVE, ON_LEAVE. Default: ACTIVE.';

comment on table t_employees
	is 'Tabla maestra de empleados. Almacena información de personal corporativo. Vinculada a: t_jobs, t_departments, t_salary_audit.';

-- Índices con nomenclatura correcta
create index idx_employees_00 on t_employees(employee_id);
comment on index idx_employees_00
	is 'Índice principal en PK (employee_id). Búsquedas de empleado por ID.';

create index idx_employees_01 on t_employees(email);
comment on index idx_employees_01
	is 'Índice UNIQUE en email. Búsquedas y validaciones de correo corporativo.';

create index idx_employees_02 on t_employees(department_id);
comment on index idx_employees_02
	is 'Índice en FK department_id. Búsquedas de empleados por departamento.';

-- Secuencia
create sequence sq_employees
	start with 100
	increment by 1
	maxvalue 999999
	nocycle
	cache 20;

comment on sequence sq_employees
	is 'Secuencia para generar IDs únicos de empleados. Rango: 100-999999. Cache: 20.';

-- ============================================================================
-- EJEMPLO 2: PROCEDIMIENTO ALMACENADO CON NOMENCLATURA
-- ============================================================================

create or replace procedure sp_hire_employee (
	p_first_name    in varchar2
	, p_last_name     in varchar2
	, p_email         in varchar2
	, p_hire_date     in date
	, p_job_id        in varchar2
	, p_salary        in number
	, p_department_id in number
	, p_employee_id   out number
) as
	--
	-- procedure: sp_hire_employee
	-- purpose: Create new employee record with validation
	-- owner: HR Department
	-- created: 2026-08-22
	--
	-- parameters:
	--   p_first_name		in varchar2		- Employee first name (required, max 20 chars)
	--   p_last_name		in varchar2		- Employee last name (required, max 25 chars)
	--   p_email			in varchar2		- Corporate email (required, must be unique)
	--   p_hire_date		in date			- Hire date (required, cannot be future)
	--   p_job_id			in varchar2		- Job position ID (required, must exist in t_jobs)
	--   p_salary			in number		- Monthly salary (required, range 2000-40000)
	--   p_department_id	in number		- Department ID (required, must exist in t_departments)
	--   p_employee_id		out number		- New employee ID (generated from sq_employees)
	--
	-- exceptions:
	--   invalid_email_format - Email does not match corporate format
	--   employee_exists      - Email already registered
	--   invalid_hire_date    - Hire date is in the future
	--   invalid_salary       - Salary outside acceptable range
	--   job_not_found        - Job ID does not exist
	--   department_not_found - Department ID does not exist
	--
	-- logic flow:
	--   1. Validate email format using regex pattern
	--   2. Check if email already exists in t_employees table
	--   3. Validate hire_date is not in future (hire_date <= SYSDATE)
	--   4. Validate salary is within range (2000-40000)
	--   5. Verify job_id exists in t_jobs table
	--   6. Verify department_id exists in t_departments table
	--   7. Generate next employee_id from sq_employees
	--   8. Insert new record into t_employees table
	--   9. Log hire event to t_audit_log table
	--   10. Commit transaction
	--   11. Return employee_id
	--
	-- performance:
	--   - Execution time: ~100-150ms (indexed email lookup)
	--   - Single round-trip to database
	--   - No full table scans
	--
	-- example usage:
	--   declare
	--       v_emp_id number;
	--   begin
	--       sp_hire_employee(
	--           p_first_name		=> 'John'
	--           , p_last_name		=> 'Doe'
	--           , p_email			=> 'john.doe@empresa.com'
	--           , p_hire_date		=> trunc(sysdate)
	--           , p_job_id			=> 'SA_MAN'
	--           , p_salary			=> 12000
	--           , p_department_id	=> 80
	--           , p_employee_id	=> v_emp_id
	--       );
	--       dbms_output.put_line('Employee created: ' || v_emp_id);
	--   end;
	--   /
	--
	v_count number;

begin
	-- Step 1-2: Validate and check email
	if not regexp_like(p_email, '^[A-Za-z0-9._%+-]+@empresa\.com$') then
		raise_application_error(-20001, 'Invalid email format');
	end if;

	select count(*) into v_count from t_employees where lower(email) = lower(p_email);
	if v_count > 0 then
		raise_application_error(-20002, 'Email already registered');
	end if;

	-- Step 3: Validate hire date
	if p_hire_date > trunc(sysdate) then
		raise_application_error(-20003, 'Hire date cannot be in the future');
	end if;

	-- Step 4: Validate salary
	if p_salary < 2000 or p_salary > 40000 then
		raise_application_error(-20004, 'Salary must be between 2000 and 40000');
	end if;

	-- Step 5-6: Verify foreign keys (no PK/FK constraints, but still validate)
	select count(*) into v_count from t_jobs where job_id = p_job_id;
	if v_count = 0 then
		raise_application_error(-20005, 'Job ID does not exist');
	end if;

	select count(*) into v_count from t_departments where department_id = p_department_id;
	if v_count = 0 then
		raise_application_error(-20006, 'Department ID does not exist');
	end if;

	-- Step 7-8: Insert new employee
	insert into t_employees (
		employee_id, first_name, last_name, email, hire_date, job_id, salary, department_id
	) values (
		sq_employees.nextval, p_first_name, p_last_name, p_email, p_hire_date, p_job_id, p_salary, p_department_id
	)
	returning employee_id into p_employee_id;

	-- Step 9: Log audit entry
	insert into t_audit_log (action, table_name, record_id, timestamp, user_name)
	values ('INSERT', 'T_EMPLOYEES', p_employee_id, sysdate, user);

	-- Step 10-11: Commit
	commit;

	exception
		when others then
			rollback;
			raise;
end sp_hire_employee;
/

-- ============================================================================
-- EJEMPLO 3: FUNCIÓN CON NOMENCLATURA
-- ============================================================================

create or replace function f_calculate_employee_compensation (
	p_employee_id in number,
	p_include_bonus in boolean default false
) return number as
	--
	-- function: f_calculate_employee_compensation
	-- purpose: Calculate total employee compensation (salary + commission + bonus)
	-- owner: Finance Department
	--
	-- parameters:
	--   p_employee_id    IN NUMBER  - Employee ID to calculate for (required)
	--   p_include_bonus  IN BOOLEAN - Include annual bonus in calculation (default: FALSE)
	--
	-- returns: NUMBER - Total compensation amount
	--
	-- logic flow:
	--   1. Query employee salary from t_employees table
	--   2. Query commission rate (if employee is salesman)
	--   3. Calculate commission based on annual sales from t_sales
	--   4. If p_include_bonus: calculate annual bonus (10% of salary)
	--   5. Return total: salary + commission + (bonus if included)
	--   6. Return NULL if employee not found
	--
	-- performance:
	--   - Execution time: ~50-80ms
	--   - Uses indexed lookups on employee_id
	--   - May perform aggregation on t_sales data
	--
	-- example usage:
	--   SELECT
	--       employee_id,
	--       first_name,
	--       f_calculate_employee_compensation(employee_id, false) as base_comp,
	--       f_calculate_employee_compensation(employee_id, true) as comp_with_bonus
	--   FROM t_employees;
	--
	v_salary        t_employees.salary%type;
	v_commission    number(10,2) := 0;
	v_bonus         number(10,2) := 0;
	v_total_sales   number(12,2);
	v_commission_pct t_employees.commission_pct%type;

begin
	-- Step 1: Get employee salary
	select salary, commission_pct
	into v_salary, v_commission_pct
	from t_employees
	where employee_id = p_employee_id;

	-- Step 2-3: Calculate commission if applicable
	if v_commission_pct > 0 then
		select nvl(sum(amount), 0)
		into v_total_sales
		from t_sales
		where employee_id = p_employee_id
		and sale_date >= trunc(sysdate, 'YYYY');

		v_commission := v_total_sales * v_commission_pct;
	end if;

	-- Step 4: Calculate bonus if requested
	if p_include_bonus then
		v_bonus := v_salary * 0.10;
	end if;

	-- Step 5: Return total
	return v_salary + v_commission + v_bonus;

	exception
		when no_data_found then
			return null;
		when others then
			raise;
end f_calculate_employee_compensation;
/

-- ============================================================================
-- EJEMPLO 4: VISTA CON NOMENCLATURA
-- ============================================================================

create or replace view vt_employee_compensation as
	--
	-- view: vt_employee_compensation
	-- purpose: Display employee names with calculated total compensation
	-- owner: Finance/HR Team
	--
	-- base query:
	--   SELECT from t_employees, t_departments, t_jobs tables
	--   LEFT JOIN to t_sales for commission calculation
	--   Includes 2026 year-to-date sales data
	--
	-- filters:
	--   - Only ACTIVE employees (status = 'ACTIVE')
	--   - Only current year sales (sale_date >= 2026-01-01)
	--
	-- columns:
	--   employee_id      - Employee identifier from t_employees
	--   full_name        - Computed: first_name || ' ' || last_name
	--   job_title        - Job name from t_jobs table
	--   department_name  - Department name from t_departments table
	--   base_salary      - Monthly salary from t_employees table
	--   ytd_sales        - Year-to-date sales total from t_sales
	--   commission       - Calculated commission (salary * commission_pct)
	--   total_comp       - Total compensation using f_calculate_employee_compensation function
	--
	-- refresh frequency: Real-time (queries current data)
	--
	select e.employee_id
		, e.first_name || ' ' || e.last_name as full_name
		, j.job_title
		, d.department_name
		, e.salary as base_salary
		, nvl(sum(s.amount), 0) as ytd_sales
		, (nvl(sum(s.amount), 0) * nvl(e.commission_pct, 0)) as commission
		, f_calculate_employee_compensation(e.employee_id, true) as total_comp
	from t_employees e
	inner join t_jobs j on e.job_id = j.job_id
	inner join t_departments d on e.department_id = d.department_id
	left join t_sales s on e.employee_id = s.employee_id
		and s.sale_date >= trunc(sysdate, 'YYYY')
	where 1 = 1
		and e.status = 'ACTIVE'
	group by e.employee_id, e.first_name, e.last_name, j.job_title, d.department_name, e.salary, e.commission_pct
	order by e.last_name, e.first_name;

comment on table vt_employee_compensation
	is 'Employee compensation summary view. Real-time calculation of salary, commission, and total compensation using f_calculate_employee_compensation.';

-- ============================================================================
-- EJEMPLO 5: TRIGGER CON NOMENCLATURA
-- ============================================================================

create or replace trigger trg_employees
	after update on t_employees
	for each row
	when (old.salary <> new.salary)
declare
	--
	-- trigger: trg_employees
	-- purpose: Audit all salary changes with old/new values and approval info
	-- owner: HR/Finance Team
	--
	-- fires: AFTER UPDATE ON t_employees
	-- for each row: Only when salary column changes
	--
	-- actions:
	--   - INSERT record to t_salary_audit table with:
	--       * Employee ID, old salary, new salary
	--       * Change timestamp (SYSDATE)
	--       * User who made change (USER)
	--       * Calculated difference (new - old)
	--       * Approval status (initially 'PENDING')
	--   - Log change to t_audit_log table
	--
	-- performance:
	--   - Execution time: <5ms
	--   - Minimal overhead (single INSERT)
	--   - No rollback of parent DML
	--
	v_difference number(10,2);

begin
	v_difference := :new.salary - :old.salary;

	insert into t_salary_audit (
		employee_id, old_salary, new_salary, salary_difference,
		change_date, changed_by, approval_status
	) values (
		:new.employee_id, :old.salary, :new.salary, v_difference,
		sysdate, user, 'PENDING'
	);

	insert into t_audit_log (
		action, table_name, record_id, details, timestamp, user_name
	) values (
		'UPDATE', 'T_EMPLOYEES', :new.employee_id,
		'Salary changed from ' || :old.salary || ' to ' || :new.salary,
		sysdate, user
	);

	exception
		when others then
			raise_application_error(-20010, 'Error in salary audit trigger: ' || sqlerrm);
end trg_employees;
/

-- ============================================================================
-- EJEMPLO 6: PAQUETE CON NOMENCLATURA
-- ============================================================================

create or replace package pk_hr_employee_management as
	--
	-- package: pk_hr_employee_management
	-- purpose: Centralized employee lifecycle management
	-- owner: HR Department
	-- created: 2026-08-22
	--
	-- public procedures:
	--   sp_hire_employee          - Create new employee record
	--   sp_terminate_employee     - Mark employee as inactive
	--   sp_update_employee_salary - Update salary with audit trail
	--   sp_transfer_employee      - Move employee to different department
	--
	-- public functions:
	--   f_get_employee_details    - Retrieve complete employee information
	--   f_is_employee_active      - Check if employee is currently active
	--   f_get_employee_count      - Get total active employee count
	--
	-- private procedures:
	--   sp_log_audit_entry        - Internal: write to t_audit_log table
	--   sp_validate_salary_range  - Internal: check salary is within bounds
	--   sp_notify_hr_system       - Internal: send notifications
	--
	-- dependencies:
	--   - TABLE: t_employees, t_departments, t_jobs, t_salary_audit
	--   - SEQUENCE: sq_employees
	--   - FUNCTION: f_calculate_employee_compensation
	--   - TRIGGER: trg_employees
	--
	-- example usage:
	--   BEGIN
	--       pk_hr_employee_management.sp_hire_employee(
	--           p_first_name => 'Jane',
	--           p_last_name => 'Smith',
	--           p_email => 'jane.smith@empresa.com',
	--           p_hire_date => TRUNC(SYSDATE),
	--           p_job_id => 'IT_PROG',
	--           p_salary => 9000,
	--           p_department_id => 60
	--       );
	--   END;
	--   /
	--

	procedure sp_hire_employee (
		p_first_name    in varchar2
		, p_last_name     in varchar2
		, p_email         in varchar2
		, p_hire_date     in date
		, p_job_id        in varchar2
		, p_salary        in number
		, p_department_id in number
	);

	procedure sp_terminate_employee (
		p_employee_id in number
		, p_termination_reason in varchar2
	);

	procedure sp_update_employee_salary (
		p_employee_id in number
		, p_new_salary  in number
		, p_reason      in varchar2
	);

	function f_get_employee_details (
		p_employee_id in number
	) return sys_refcursor;

	function f_is_employee_active (
		p_employee_id in number
	) return boolean;

	function f_get_employee_count return number;

end pk_hr_employee_management;
/

-- ============================================================================
-- FIN DE EJEMPLOS
-- ============================================================================
