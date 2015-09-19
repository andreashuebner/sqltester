CREATE TABLE tbl_testing_683657484 as select count(*) as number_duplicates, case when count(*) > 0 then "Duplicates found in table tbl_customers3" else "" end as error_description from ( SELECT account_id2, COUNT(*) FROM tbl_customers3 GROUP BY account_id2 HAVING COUNT(*) > 1 )x ;


CREATE TABLE tbl_testing_aggregation_163573299 as
select
error_description
from tbl_testing_683657484
where error_description != ''
;
