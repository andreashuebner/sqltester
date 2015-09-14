CREATE TABLE tbl_testing_585250248 as select count(*) as number_duplicates, case when count(*) > 0 then "Duplicates found in table tbl_customers" else "" end as error_description from ( SELECT account_id, COUNT(*) FROM tbl_customers GROUP BY account_id HAVING COUNT(*) > 1 )x ;

CREATE TABLE tbl_testing_638051118 as select count(*) as number_duplicates, case when count(*) > 0 then "Duplicates found in table tbl_customers2" else "" end as error_description from ( SELECT account_id2, COUNT(*) FROM tbl_customers2 GROUP BY account_id2 HAVING COUNT(*) > 1 )x ;

CREATE TABLE tbl_testing_259211361 as select case when number_datasets < 100 then "Expected at least 100 datasets in table tbl_customers" else "" end as error_description from ( SELECT COUNT(*) as number_datasets FROM tbl_customers )x ;

CREATE TABLE tbl_testing_749661705 as select case when number_datasets < 200 then "Expected at least 200 datasets in table tbl_customers" else "" end as error_description from ( SELECT COUNT(*) as number_datasets FROM tbl_customers where invoice_amount >= 100 and invoice_age <= 30 )x ;

CREATE TABLE tbl_testing_750172814 as select case when sum_of_field < 1000 then "Expected sum of invoice_amount in table tbl_customers to be at least 1000" else "" end as error_description from ( SELECT SUM(invoice_amount) as sum_of_field FROM tbl_customers )x ;

CREATE TABLE tbl_testing_359180149 as select case when sum_of_field < 1000 then "Expected sum of invoice_amount in table tbl_customers to be at least 1000" else "" end as error_description from ( SELECT SUM(invoice_amount) as sum_of_field FROM tbl_customers where invoice_amount >= 100 and invoice_age <= 30 )x ;


CREATE TABLE tbl_testing_aggregation_54737853 as
select
error_description
from tbl_testing_585250248,tbl_testing_638051118,tbl_testing_259211361,tbl_testing_749661705,tbl_testing_750172814,tbl_testing_359180149
where error_description != ''
;
